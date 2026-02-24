# 🧮 ML Calculator Feature - Team Dashboard

## ✅ NEW FEATURE ADDED!

A new **ML Calculator** tab has been added to the Team Dashboard, allowing teams to manually input player statistics and get AI-powered price predictions.

---

## 📍 Location

**Team Dashboard** → **ML Calculator Tab** (4th tab)

Access: http://localhost:8000/team-dashboard (after team login)

---

## 🎯 Features

### 1. Manual Input Form
Teams can enter custom player statistics:
- **Matches Played** (e.g., 100)
- **Batting Average** (e.g., 35.5)
- **Strike Rate** (e.g., 130.0)
- **Wickets Taken** (e.g., 15)
- **Economy Rate** (e.g., 8.0)
- **Recent Performance Score** (0-100, e.g., 75)
- **Player Type** (Batsman/Bowler/All-Rounder/Wicketkeeper)

### 2. Real-time Predictions
- Click "Calculate Prediction" button
- AI model processes the input
- Shows predicted auction price
- Displays confidence range (±15%)
- Shows input summary

### 3. Model Information
- Model name (Random Forest)
- Accuracy (75.31%)
- Number of features (7)
- Training timestamp

### 4. Interactive UI
- Beautiful gradient design
- Smooth animations
- Loading states
- Error handling
- Reset functionality

---

## 🎨 UI Components

### Input Section (Left)
```
┌─────────────────────────────┐
│ Player Statistics           │
├─────────────────────────────┤
│ Matches Played: [100]       │
│ Batting Average: [35.0]     │
│ Strike Rate: [130.0]        │
│ Wickets: [15]               │
│ Economy Rate: [8.0]         │
│ Performance: [75]           │
│ Player Type: [Batsman ▼]    │
│                             │
│ [Calculate Prediction]      │
│ [Reset Form]                │
└─────────────────────────────┘
```

### Results Section (Right)
```
┌─────────────────────────────┐
│ Prediction Results          │
├─────────────────────────────┤
│ ╔═══════════════════════╗  │
│ ║ Predicted Price       ║  │
│ ║   ₹17,50,000         ║  │
│ ║ Model: RANDOM FOREST  ║  │
│ ╚═══════════════════════╝  │
│                             │
│ Confidence Range (±15%)     │
│ Min: ₹14,87,500            │
│ Max: ₹20,12,500            │
│                             │
│ Input Statistics            │
│ Matches: 100                │
│ Batting Avg: 35.0           │
│ ...                         │
└─────────────────────────────┘
```

---

## 🚀 How to Use

### Step 1: Access Team Dashboard
1. Login as a team
2. Go to Team Dashboard
3. Click on "🤖 ML Calculator" tab

### Step 2: Enter Statistics
1. Fill in player statistics
2. Adjust values as needed
3. Select player type from dropdown

### Step 3: Calculate
1. Click "Calculate Prediction"
2. Wait for AI processing (1-2 seconds)
3. View predicted price and confidence range

### Step 4: Analyze Results
- Check predicted price
- Review confidence range
- Compare with your budget
- Plan bidding strategy

### Step 5: Test Scenarios
- Try different stat combinations
- See how stats affect price
- Find optimal player profiles
- Click "Reset Form" to start over

---

## 💡 Use Cases

### 1. Pre-Auction Planning
- Test different player profiles
- Understand price ranges
- Plan budget allocation
- Identify value players

### 2. Bidding Strategy
- Estimate fair prices
- Set maximum bid limits
- Compare similar players
- Make informed decisions

### 3. Player Evaluation
- Assess player worth
- Compare stats vs price
- Find undervalued players
- Avoid overpaying

### 4. What-If Analysis
- "What if batting avg is 40 instead of 35?"
- "How much is a wicketkeeper worth?"
- "Does strike rate matter more than average?"
- Test hypothetical scenarios

---

## 📊 Example Scenarios

### Scenario 1: Star Batsman
```
Input:
- Matches: 150
- Batting Avg: 45.5
- Strike Rate: 150.0
- Wickets: 5
- Economy: 9.0
- Performance: 90
- Type: Batsman

Output:
- Predicted: ₹22,50,000
- Range: ₹19,12,500 - ₹25,87,500
```

### Scenario 2: Economical Bowler
```
Input:
- Matches: 100
- Batting Avg: 15.0
- Strike Rate: 100.0
- Wickets: 120
- Economy: 6.5
- Performance: 85
- Type: Bowler

Output:
- Predicted: ₹18,75,000
- Range: ₹15,93,750 - ₹21,56,250
```

### Scenario 3: All-Rounder
```
Input:
- Matches: 120
- Batting Avg: 35.0
- Strike Rate: 135.0
- Wickets: 80
- Economy: 8.0
- Performance: 88
- Type: All-Rounder

Output:
- Predicted: ₹21,00,000
- Range: ₹17,85,000 - ₹24,15,000
```

---

## 🎯 Benefits

### For Teams
- ✅ Make data-driven decisions
- ✅ Avoid overpaying
- ✅ Find value players
- ✅ Plan budget effectively
- ✅ Test scenarios before bidding

### For Strategy
- ✅ Understand price factors
- ✅ Compare player types
- ✅ Optimize squad composition
- ✅ Maximize ROI

---

## 🔧 Technical Details

### API Endpoint
```
POST /ml/predict-price
```

### Request Format
```json
{
  "matches_played": 100,
  "batting_average": 35.0,
  "strike_rate": 130.0,
  "wickets": 15,
  "economy_rate": 8.0,
  "recent_performance_score": 75.0,
  "player_type": "Batsman"
}
```

### Response Format
```json
{
  "success": true,
  "predicted_price": 1750000.0,
  "predicted_price_formatted": "₹17,50,000.00",
  "model_used": "random_forest",
  "confidence_range": {
    "min": 1487500.0,
    "max": 2012500.0,
    "min_formatted": "₹14,87,500.00",
    "max_formatted": "₹20,12,500.00"
  }
}
```

---

## 🎨 Design Features

- **Purple Gradient Theme**: Matches ML branding
- **Smooth Animations**: Fade-in effects
- **Loading States**: Spinner during calculation
- **Error Handling**: Clear error messages
- **Responsive Design**: Works on mobile
- **Intuitive Layout**: Two-column design
- **Visual Feedback**: Toast notifications

---

## ✅ Status

**Feature**: LIVE and WORKING  
**Server**: http://localhost:8000  
**Access**: Team Dashboard → ML Calculator Tab

---

**Last Updated**: February 22, 2026, 5:21 PM  
**Version**: 1.1.0 (ML Calculator Added)
