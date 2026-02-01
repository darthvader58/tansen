#!/bin/bash
# Security Verification Script

echo "🔒 Security Verification for Tansen Music Transcription Backend"
echo "================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if sensitive files exist
echo "📁 Checking for sensitive files..."
SENSITIVE_FILES=(
    "backend/.env"
    "backend/tansen-melody-firebase-adminsdk-fbsvc-21c81e4b77.json"
    "google-services.json"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} Found: $file"
    else
        echo -e "${RED}✗${NC} Missing: $file"
    fi
done

echo ""
echo "🚫 Checking if sensitive files are in .gitignore..."

# Check .gitignore
if grep -q "\.env" .gitignore && grep -q "firebase-adminsdk" .gitignore; then
    echo -e "${GREEN}✓${NC} .gitignore properly configured"
else
    echo -e "${RED}✗${NC} .gitignore missing sensitive file patterns"
fi

echo ""
echo "📝 Checking if sensitive files are tracked by git..."

# Check if files are tracked
TRACKED=$(git ls-files | grep -E "(\.env$|firebase-adminsdk|google-services\.json)" | grep -v "\.example" || true)

if [ -z "$TRACKED" ]; then
    echo -e "${GREEN}✓${NC} No sensitive files tracked by git"
else
    echo -e "${RED}✗${NC} WARNING: Sensitive files tracked by git:"
    echo "$TRACKED"
    echo ""
    echo "To remove from git (but keep locally):"
    echo "  git rm --cached <filename>"
fi

echo ""
echo "🔑 Checking environment variables..."

# Check if .env has required variables
if [ -f "backend/.env" ]; then
    REQUIRED_VARS=("FIREBASE_PROJECT_ID" "FIREBASE_STORAGE_BUCKET" "JWT_SECRET_KEY")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" backend/.env; then
            echo -e "${GREEN}✓${NC} $var is set"
        else
            echo -e "${RED}✗${NC} $var is missing"
        fi
    done
else
    echo -e "${RED}✗${NC} backend/.env not found"
fi

echo ""
echo "🔐 Security Recommendations:"
echo "  1. Never commit .env or *-firebase-adminsdk-*.json files"
echo "  2. Rotate Firebase credentials every 90 days"
echo "  3. Use different Firebase projects for dev/staging/prod"
echo "  4. Enable App Check in Firebase Console"
echo "  5. Deploy Firestore and Storage security rules"
echo "  6. Set up monitoring and alerts"
echo "  7. Enable 2FA on your Google account"
echo ""

# Check if Firebase CLI is installed
if command -v firebase &> /dev/null; then
    echo -e "${GREEN}✓${NC} Firebase CLI installed"
    echo ""
    echo "📤 To deploy security rules:"
    echo "  firebase deploy --only firestore:rules"
    echo "  firebase deploy --only storage:rules"
else
    echo -e "${YELLOW}⚠${NC}  Firebase CLI not installed"
    echo "  Install with: npm install -g firebase-tools"
fi

echo ""
echo "================================================================"
echo "Security check complete!"
