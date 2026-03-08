# Manual Price Feature Testing Guide

## Quick Test Scenarios

### 1. Manual Price Setting Test
1. Start both backend and frontend servers
2. Login to the application
3. Navigate to the Assets page
4. Click the "设置价格" button on any asset
5. Enter a new price (e.g., 100.50)
6. Click "确定"
7. Verify:
   - Success message appears
   - Price updates in the table
   - Price shows in orange color
   - "手动" badge appears
   - Timestamp shows current time

### 2. API Refresh Test (Preserve Manual Price)
1. Set a manual price on an asset
2. Note the current time
3. Click the "刷新" button on the same asset
4. Verify:
   - Manual price is preserved (if < 24 hours old)
   - Price difference is < 5%
   - Manual badge remains visible
   - Timestamp doesn't change

### 3. API Override Test (Time-based)
1. Set a manual price on an asset
2. Manually update the database to set `manual_set_at` to 25 hours ago
   ```sql
   UPDATE assets
   SET manual_set_at = datetime('now', '-25 hours')
   WHERE id = <asset_id>;
   ```
3. Click the "刷新" button
4. Verify:
   - Price updates to API price
   - Manual badge disappears
   - Price shows in green color

### 4. API Override Test (Difference-based)
1. Set a manual price significantly different from API price (e.g., set 200 when API is 100)
2. Click the "刷新" button
3. Verify:
   - Price updates to API price
   - Manual badge disappears
   - Price shows in green color

### 5. Batch Refresh Test
1. Set manual prices on multiple assets
2. Click the "刷新数据" button in the header
3. Verify:
   - System applies smart logic to each asset
   - Some prices may change, others preserved
   - Consistent behavior with individual refresh

### 6. Force Refresh Test
1. Set a manual price on an asset
2. Access the API directly with `?refresh=true` parameter
   ```bash
   curl "http://localhost:8000/assets?refresh=true"
   ```
3. Verify:
   - Forces override even if manual price is recent
   - All prices update to API prices

## API Testing Examples

### Set Manual Price
```bash
curl -X PUT "http://localhost:8000/assets/1/current-price" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "manual_set_price": 150.25
  }'
```

### Get Assets (Normal)
```bash
curl "http://localhost:8000/assets" \
  -H "Authorization: Bearer <your_token>"
```

### Get Assets (Force Refresh)
```bash
curl "http://localhost:8000/assets?refresh=true" \
  -H "Authorization: Bearer <your_token>"
```

### Refresh Single Asset
```bash
curl -X POST "http://localhost:8000/assets/1/refresh" \
  -H "Authorization: Bearer <your_token>"
```

### Batch Refresh
```bash
curl -X POST "http://localhost:8000/assets/batch-refresh" \
  -H "Authorization: Bearer <your_token>"
```

## Expected Responses

### Success Response (Set Manual Price)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "600519",
    "name": "贵州茅台",
    "current_price": 150.25,
    "is_manually_set": true,
    "manual_set_price": 150.25,
    "manual_set_at": "2026-03-08T14:30:00",
    "market_value": 15025.0,
    "profit": 5025.0,
    "profit_percent": 50.25
  }
}
```

### Error Response (Invalid Price)
```json
{
  "detail": "手动设置的价格必须大于0"
}
```

## Visual Verification Checklist

- [ ] Manual prices display in orange color
- [ ] API prices display in green color
- [ ] "手动" badge appears for manual prices
- [ ] Timestamp shows for manual prices
- [ ] Price dialog shows current price type badge
- [ ] "设置价格" button works in table
- [ ] Price input accepts decimal values
- [ ] Form validation rejects invalid prices
- [ ] Success message appears on save
- [ ] Error message appears on failure

## Database Verification

After setting a manual price, verify the database:

```bash
sqlite3 backend/db/bafangce.db "SELECT code, current_price, is_manually_set, manual_set_price, manual_set_at FROM assets WHERE id = 1;"
```

Expected output:
```
600519|150.25|1|150.25|2026-03-08 14:30:00
```

## Edge Cases to Test

1. **Zero or negative price:** Should be rejected with validation error
2. **Very large price:** Should be accepted if valid
3. **Multiple rapid updates:** Latest update should persist
4. **Concurrent updates:** Database should handle gracefully
5. **Network errors during update:** Should show error message
6. **Asset not found:** Should return 404 error
7. **Unauthorized access:** Should return 401/403 error

## Performance Considerations

- Manual price operations are single-row updates (fast)
- Batch refresh processes assets sequentially
- Smart override logic adds minimal overhead (< 1ms per asset)
- Database indexes on user_id and code ensure fast queries

---

**Note:** Ensure you have valid authentication tokens before testing API endpoints directly.
