"""
Security Dashboard API
Provides endpoints for security monitoring and management.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict
from datetime import datetime, timezone

from core.security_monitor import security_monitor
from core.auto_blocker import auto_blocker
from core.auth_middleware import StrictAuthMiddleware

router = APIRouter(prefix="/api/security", tags=["security"])


def require_admin(request: Request):
    """Require admin authentication."""
    if not getattr(request.state, "is_admin", False):
        raise HTTPException(403, "Admin access required")
    return request.state


@router.get("/stats")
async def get_security_stats(request: Request, _=Depends(require_admin)):
    """
    Get security statistics for dashboard.
    Requires admin authentication.
    """
    monitor_stats = security_monitor.get_security_stats()
    blocker_stats = auto_blocker.get_stats()
    
    return {
        "timestamp": datetime.now(timezone.utc),
        "monitoring": monitor_stats,
        "blocking": blocker_stats
    }


@router.get("/events")
async def get_security_events(
    request: Request,
    limit: int = 50,
    severity: str = None,
    _=Depends(require_admin)
):
    """
    Get recent security events.
    Requires admin authentication.
    """
    from database import db
    
    query = {}
    if severity:
        query["severity"] = severity
    
    events = list(
        db.security_events
        .find(query)
        .sort("timestamp", -1)
        .limit(limit)
    )
    
    # Convert ObjectId to string
    for event in events:
        event["_id"] = str(event["_id"])
        event["timestamp"] = event["timestamp"].isoformat()
    
    return {
        "events": events,
        "total": len(events)
    }


@router.get("/blocked-ips")
async def get_blocked_ips(request: Request, _=Depends(require_admin)):
    """
    Get all currently blocked IPs.
    Requires admin authentication.
    """
    blocked = auto_blocker.get_blocked_ips()
    
    # Convert datetime to ISO format
    for block in blocked:
        block["blocked_at"] = block["blocked_at"].isoformat()
        block["expires_at"] = block["expires_at"].isoformat()
    
    return {
        "blocked_ips": blocked,
        "total": len(blocked)
    }


@router.post("/block-ip")
async def block_ip(
    request: Request,
    ip: str,
    reason: str,
    duration_hours: int = 24,
    _=Depends(require_admin)
):
    """
    Manually block an IP address.
    Requires admin authentication.
    """
    auto_blocker.block_ip(
        ip=ip,
        reason=f"Manual block by admin: {reason}",
        duration_hours=duration_hours,
        severity="high"
    )
    
    return {
        "success": True,
        "message": f"IP {ip} blocked for {duration_hours} hours"
    }


@router.post("/unblock-ip")
async def unblock_ip(
    request: Request,
    ip: str,
    _=Depends(require_admin)
):
    """
    Manually unblock an IP address.
    Requires admin authentication.
    """
    auto_blocker.unblock_ip(ip)
    
    return {
        "success": True,
        "message": f"IP {ip} unblocked"
    }


@router.get("/check-ip/{ip}")
async def check_ip_status(
    request: Request,
    ip: str,
    _=Depends(require_admin)
):
    """
    Check if an IP is blocked and get details.
    Requires admin authentication.
    """
    is_blocked = auto_blocker.is_blocked(ip)
    is_suspicious = security_monitor.is_suspicious_ip(ip)
    failed_logins = security_monitor.get_failed_login_count(ip)
    
    block_info = None
    if is_blocked:
        block_info = auto_blocker.get_block_info(ip)
        if block_info:
            block_info["blocked_at"] = block_info["blocked_at"].isoformat()
            block_info["expires_at"] = block_info["expires_at"].isoformat()
    
    return {
        "ip": ip,
        "is_blocked": is_blocked,
        "is_suspicious": is_suspicious,
        "failed_login_attempts": failed_logins,
        "block_info": block_info
    }


@router.post("/cleanup")
async def cleanup_security_data(
    request: Request,
    days: int = 90,
    _=Depends(require_admin)
):
    """
    Clean up old security events and expired blocks.
    Requires admin authentication.
    """
    events_deleted = security_monitor.cleanup_old_events(days)
    blocks_deleted = auto_blocker.cleanup_expired_blocks()
    
    return {
        "success": True,
        "events_deleted": events_deleted,
        "blocks_deleted": blocks_deleted
    }
