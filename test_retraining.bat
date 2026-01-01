# Testing Model Retraining - Verification Script

## Step 1: Check Initial State
echo "=== STEP 1: Checking Initial Model File ==="
if exist data\ml_model.joblib (
    echo ✓ Model file exists
    dir /T:W data\ml_model.joblib
) else (
    echo ✗ Model file NOT found - Model needs to be trained first
)
echo.

## Step 2: Instructions
echo "=== STEP 2: Manual Testing Steps ==="
echo.
echo 1. Open your UI at http://localhost:3000
echo 2. Ask: "Calculate 10 + 5"
echo 3. Click "Helpful" button
echo 4. Watch your Python terminal for retraining logs
echo.
echo Expected Terminal Output:
echo   ============================================================
echo   [META-LEARNING] 🧠 POSITIVE FEEDBACK RECEIVED!
echo   [META-LEARNING] 🔄 Triggering automatic model retraining...
echo   ============================================================
echo   [META-LEARNING] Fetched X recent experiences for training
echo   Model successfully retrained with X new examples.
echo   ============================================================
echo   [META-LEARNING] ✅ Auto-learning complete!
echo   ============================================================
echo.
echo 5. Press any key to check if model file was updated...
pause > nul

## Step 3: Check Updated State
echo.
echo "=== STEP 3: Checking Model File After Feedback ==="
if exist data\ml_model.joblib (
    echo ✓ Model file still exists
    dir /T:W data\ml_model.joblib
    echo.
    echo Compare the timestamp above with Step 1.
    echo If different: ✅ RETRAINING WORKED!
    echo If same: ❌ RETRAINING FAILED - Check logs
) else (
    echo ✗ Model file disappeared - Something is wrong!
)
echo.

echo "=== STEP 4: Check Database ==="
echo Open Supabase Dashboard and verify:
echo   1. New entry in "experiences" table
echo   2. Feedback column = 1 (for helpful)
echo   3. Strategy column matches what you saw in UI
echo.
pause
