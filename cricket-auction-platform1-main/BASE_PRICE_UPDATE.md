# Base Price Update - Manual Entry

## Changes Made

### 1. Player Registration Form (User Dashboard)
**Added manual base price input field**:
- Field name: "Base Price (Starting Bid)"
- Required field (marked with red asterisk)
- Minimum value: ₹10,000
- Step: ₹1,000
- Placeholder: "e.g., 50000"
- Help text: "Minimum ₹10,000 - This is your starting auction price"

**Location**: Between "Bowling Style" and "Profile Photo" fields

### 2. Backend API (routers/players.py)
**Updated `/players/public_register` endpoint**:
- Added `base_price: int = Form(...)` parameter (mandatory)
- Added validation: base_price must be >= ₹10,000
- Removed auto-calculation based on category (Faculty/Student/Alumni)
- Now uses the manual base_price value from the form
- Updated success message to show the entered base price

**Before**:
```python
# Auto-calculated based on category
default_base_prices = {
    "Faculty": 75000,
    "Student": 50000,
    "Alumni": 60000
}
default_base_price = default_base_prices.get(category, 50000)
```

**After**:
```python
# Manual entry with validation
if not base_price or base_price < 10000:
    raise HTTPException(
        status_code=400,
        detail="Base price must be at least ₹10,000"
    )
# Use the manual base_price directly
```

### 3. Admin Panel (Already Exists)
**Admin can edit base price** via:
- **UI**: "Pending Players (Set Base Price)" section
- **Endpoint**: `PATCH /admin/player/{player_id}/base-price`
- **Input**: Number field with "₹" prefix
- **Button**: "Set" button to save

**How it works**:
1. Admin sees list of pending players
2. Each player has an input field for base price
3. Admin enters price and clicks "Set"
4. API updates the player's base_price in database
5. Success message shown

## User Flow

### For Players (Self-Registration)
1. Login as user
2. Click "Register as a Player"
3. Fill in all details including:
   - Name, role, category, age, styles
   - **Base Price** (e.g., ₹50,000)
   - Photo (mandatory, max 500KB)
   - Bio
4. Submit registration
5. Player is auto-approved with the entered base price

### For Admin (Edit Base Price)
1. Login as admin
2. Go to "Player Management" tab
3. See "Pending Players (Set Base Price)" section
4. Enter new base price for any player
5. Click "Set" to update
6. Player's base price is updated immediately

## Validation Rules

### Player Registration
- Base price is **required** (cannot be empty)
- Minimum value: **₹10,000**
- Must be a valid number
- Increments of ₹1,000 (step value)

### Admin Edit
- Base price must be > 0
- No maximum limit
- Can edit any player's base price at any time

## Benefits

1. **Flexibility**: Players can set their own starting bid based on their skills
2. **Fairness**: No automatic categorization that might undervalue/overvalue players
3. **Control**: Admin can adjust prices if needed
4. **Transparency**: Players know exactly what their starting bid will be

## Technical Details

### Database Field
- Field: `base_price` (integer)
- Status: `base_price_status` ("approved" for auto-approved players)
- Updated: `updated_at` timestamp

### API Endpoints

#### Player Registration
```
POST /players/public_register
Form Data:
  - full_name: string (required)
  - role: string (required)
  - category: string (optional)
  - base_price: integer (required, min 10000)
  - age: integer (optional)
  - batting_style: string (optional)
  - bowling_style: string (optional)
  - bio: string (optional)
  - photo: file (required, max 500KB)
```

#### Admin Edit Base Price
```
PATCH /admin/player/{player_id}/base-price
Body:
  {
    "price": 50000
  }
```

## Testing

### Test Player Registration
1. Go to http://localhost:8000
2. Register as user
3. Click "Register as a Player"
4. Try entering base price < ₹10,000 → Should show error
5. Enter valid base price (e.g., ₹50,000)
6. Complete registration → Should succeed

### Test Admin Edit
1. Login as admin
2. Go to Player Management
3. Find a player in pending list
4. Enter new base price
5. Click "Set" → Should update successfully

## Migration Notes

### Existing Players
- Players registered before this update may have auto-calculated base prices
- Admin can edit these prices using the admin panel
- No data migration needed

### New Players
- All new registrations require manual base price entry
- No default values applied
- Players must consciously choose their starting bid

## Summary

Players now have full control over their starting auction price during registration, with a minimum of ₹10,000. Admins retain the ability to adjust any player's base price through the admin panel. This provides flexibility while maintaining oversight.
