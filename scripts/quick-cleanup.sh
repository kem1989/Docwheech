#!/bin/bash
# Quick database cleanup script
# Deletes all submissions, documents, and ACORD data
# Preserves user accounts

echo "🗑️  Cleaning database..."

docker exec -i docwheech_postgres psql -U docwheech_user -d docwheech << 'EOF'
-- Delete all extraction data (preserve users)
DELETE FROM losses;
DELETE FROM loss_histories;
DELETE FROM signatures;
DELETE FROM prior_carriers;
DELETE FROM premises;
DELETE FROM nature_of_business;
DELETE FROM contacts;
DELETE FROM first_named_insureds;
DELETE FROM lines_of_business;
DELETE FROM policies;
DELETE FROM transaction_statuses;
DELETE FROM agencies;
DELETE FROM documents;
DELETE FROM submissions;

-- Show final counts
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM submissions) as submissions,
    (SELECT COUNT(*) FROM documents) as documents,
    (SELECT COUNT(*) FROM agencies) as agencies,
    (SELECT COUNT(*) FROM contacts) as contacts,
    (SELECT COUNT(*) FROM first_named_insureds) as insureds,
    (SELECT COUNT(*) FROM policies) as policies;

SELECT '✅ Database cleaned successfully!' as status;
EOF

echo ""
echo "✅ Cleanup complete!"

