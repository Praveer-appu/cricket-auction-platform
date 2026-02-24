# Player Photo Upload Requirements

## Summary
Player registration now requires a mandatory profile photo with size restrictions.

## Changes Made

### 1. Frontend Validation (user_dashboard.html)
- **Mandatory Photo**: Photo field is now required (`required` attribute)
- **Size Validation**: Client-side validation enforces 500KB maximum
- **Real-time Feedback**: Shows file size error immediately on file selection
- **Visual Indicator**: Red asterisk (*) marks photo as required field
- **Preview Feature**: Shows photo preview before submission

### 2. Backend Validation (routers/players.py)
- **Mandatory Parameter**: Changed `photo: Optional[UploadFile] = File(None)` to `photo: UploadFile = File(...)`
- **Size Check**: Server validates file size is under 500KB (500 * 1024 bytes)
- **Type Validation**: Only JPG, PNG, and WebP formats allowed
- **Error Messages**: Clear error messages with actual file size shown
- **Storage**: 
  - Primary: Cloudinary (for production/Railway)
  - Fallback: Local storage at `static/uploads/players/` (for development)

### 3. Team Dashboard Display
- **Player Cards**: Already displays player photos in grid view
- **Detail Modal**: Shows full-size photo when clicking on player card
- **Fallback**: Shows default avatar icon if photo missing
- **Responsive**: Photos scale properly on all devices

## Validation Rules

### File Size
- **Maximum**: 500KB (512,000 bytes)
- **Validation**: Both client-side (JavaScript) and server-side (Python)
- **Error Message**: "Photo size must be less than 500KB. Your photo is XXX KB. Please compress or choose a smaller photo."

### File Type
- **Allowed**: JPG, JPEG, PNG, WebP
- **Validation**: Server checks MIME type
- **Error Message**: "Invalid image type. Only JPG, PNG, and WebP are allowed."

### Required Field
- **Status**: Mandatory for all new player registrations
- **Validation**: HTML5 `required` attribute + JavaScript check
- **Error Message**: "Please upload your profile photo. It is mandatory for registration."

## User Experience

### Registration Flow
1. User fills player registration form
2. User selects photo file
3. System validates size immediately (< 500KB)
4. Preview shows if valid, error shown if too large
5. On submit, validates photo is present
6. Server validates size and type again
7. Photo uploaded to Cloudinary or local storage
8. Player registered with photo URL

### Team Owner View
1. Team owners see player photos in grid view
2. Click on player card to see full profile
3. Modal shows large photo with all player details
4. Photos load from Cloudinary or local storage

## Technical Details

### Storage Locations
- **Production (Railway)**: Cloudinary CDN (requires env vars)
- **Development (Local)**: `static/uploads/players/` directory
- **URL Format**: 
  - Cloudinary: `https://res.cloudinary.com/...`
  - Local: `/static/uploads/players/player_xxxxx.jpg`

### Environment Variables (Production)
```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### File Naming
- **Pattern**: `player_{uuid}.{extension}`
- **Example**: `player_a1b2c3d4e5f6.jpg`
- **Uniqueness**: UUID ensures no conflicts

## Testing

### Test Cases
1. ✅ Register without photo → Error: "Please upload your profile photo"
2. ✅ Upload photo > 500KB → Error: "Photo size must be less than 500KB"
3. ✅ Upload invalid format (PDF, etc.) → Error: "Invalid image type"
4. ✅ Upload valid photo < 500KB → Success with photo displayed
5. ✅ View player in team dashboard → Photo displays correctly
6. ✅ Click player card → Modal shows full photo and details

### How to Test
1. Go to http://localhost:8000
2. Login as user (or register new account)
3. Click "Register as a Player"
4. Try uploading photos of different sizes
5. Verify validation messages
6. Complete registration with valid photo
7. Login as team owner (virat/virat123)
8. Verify player photo displays in dashboard

## Notes
- Cloudinary is recommended for production (Railway) as filesystem is ephemeral
- Local storage works for development but files will be lost on Railway restart
- Photos are automatically resized/optimized by Cloudinary
- Team dashboard already had photo display functionality - no changes needed there
