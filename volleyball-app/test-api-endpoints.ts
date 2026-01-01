/**
 * API Endpoint Verification Script
 * 
 * This script tests all API endpoints to ensure they return the correct data structure.
 * Run with: npx ts-node test-api-endpoints.ts
 * 
 * Or in development:
 * 1. Copy this file to app/test-api-endpoints.ts
 * 2. Add a useEffect in the root screen to call testAllEndpoints()
 * 3. Check console for test results
 */

import { apiClient } from './app/api/client';

interface TestResult {
  endpoint: string;
  status: 'PASS' | 'FAIL';
  message: string;
  data?: any;
}

const results: TestResult[] = [];

async function testEndpoint(
  name: string,
  testFn: () => Promise<any>,
  validator: (data: any) => { valid: boolean; error?: string }
) {
  try {
    console.log(`\n🧪 Testing: ${name}`);
    const response = await testFn();

    const validation = validator(response);
    if (validation.valid) {
      console.log(`✅ ${name}: PASS`);
      results.push({
        endpoint: name,
        status: 'PASS',
        message: 'Data structure is correct',
        data: response,
      });
    } else {
      console.log(`❌ ${name}: FAIL - ${validation.error}`);
      results.push({
        endpoint: name,
        status: 'FAIL',
        message: validation.error || 'Unknown error',
        data: response,
      });
    }
  } catch (error: any) {
    console.log(`❌ ${name}: ERROR - ${error.message}`);
    results.push({
      endpoint: name,
      status: 'FAIL',
      message: error.message,
    });
  }
}

async function testAllEndpoints() {
  console.log('='.repeat(60));
  console.log('🚀 Starting API Endpoint Verification');
  console.log('='.repeat(60));

  // Test Login Endpoint
  await testEndpoint(
    'POST /login/',
    () => apiClient.login('jsmith', 'password123'),
    (data) => {
      if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Response is not an object' };
      }
      if (!data.token || !data.user) {
        return { valid: false, error: 'Missing token or user field' };
      }
      if (!data.user.id || !data.user.username) {
        return { valid: false, error: 'User missing required fields' };
      }
      return { valid: true };
    }
  );

  // Test Player Profile Endpoint
  await testEndpoint(
    'GET /player/profile/',
    () => apiClient.getPlayerProfile(),
    (data) => {
      if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Response is not an object' };
      }
      if (!data.data) {
        return { valid: false, error: 'Response missing .data wrapper' };
      }
      if (!data.data.id) {
        return { valid: false, error: 'Profile missing id field' };
      }
      return { valid: true };
    }
  );

  // Test Player Stats Endpoint
  await testEndpoint(
    'GET /player/stats/',
    () => apiClient.getPlayerStats(),
    (data) => {
      if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Response is not an object' };
      }
      if (!data.data) {
        return { valid: false, error: 'Response missing .data wrapper' };
      }
      if (typeof data.data.kills !== 'number' || typeof data.data.blocks !== 'number') {
        return { valid: false, error: 'Stats missing numeric fields' };
      }
      return { valid: true };
    }
  );

  // Test AI Summary Endpoint
  await testEndpoint(
    'GET /player/summary/',
    () => apiClient.getAISummary(),
    (data) => {
      if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Response is not an object' };
      }
      if (!data.data) {
        return { valid: false, error: 'Response missing .data wrapper' };
      }
      if (!data.data.summary || typeof data.data.summary !== 'string') {
        return { valid: false, error: 'Summary missing or not a string' };
      }
      return { valid: true };
    }
  );

  // Test Announcements Endpoint
  await testEndpoint(
    'GET /announcements/',
    () => apiClient.getAnnouncements(),
    (data) => {
      if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Response is not an object' };
      }
      if (!data.data || !Array.isArray(data.data)) {
        return { valid: false, error: 'Response missing .data or it\'s not an array' };
      }
      if (data.data.length > 0) {
        const first = data.data[0];
        if (!first.id || !first.title || !first.message) {
          return { valid: false, error: 'Announcement missing required fields (id, title, message)' };
        }
        if (typeof first.is_urgent !== 'boolean') {
          return { valid: false, error: 'Announcement missing is_urgent boolean field' };
        }
      }
      return { valid: true };
    }
  );

  // Test Videos Endpoint
  await testEndpoint(
    'GET /videos/',
    () => apiClient.getGameVideos(),
    (data) => {
      if (!data || typeof data !== 'object') {
        return { valid: false, error: 'Response is not an object' };
      }
      if (!data.data || !Array.isArray(data.data)) {
        return { valid: false, error: 'Response missing .data or it\'s not an array' };
      }
      if (data.data.length > 0) {
        const first = data.data[0];
        if (!first.id || !first.title) {
          return { valid: false, error: 'Video missing required fields (id, title)' };
        }
      }
      return { valid: true };
    }
  );

  // Print Summary
  console.log('\n' + '='.repeat(60));
  console.log('📊 Test Results Summary');
  console.log('='.repeat(60));

  const passed = results.filter((r) => r.status === 'PASS').length;
  const failed = results.filter((r) => r.status === 'FAIL').length;

  results.forEach((result) => {
    const icon = result.status === 'PASS' ? '✅' : '❌';
    console.log(`${icon} ${result.endpoint}: ${result.message}`);
  });

  console.log('\n' + '='.repeat(60));
  console.log(`Total: ${results.length} | Passed: ${passed} | Failed: ${failed}`);
  console.log('='.repeat(60) + '\n');

  if (failed === 0) {
    console.log('🎉 All tests passed! API endpoints are working correctly.');
  } else {
    console.log(`⚠️  ${failed} test(s) failed. Review the errors above.`);
  }

  return {
    total: results.length,
    passed,
    failed,
    results,
  };
}

// Export for use in tests
export { results, testAllEndpoints };

// Uncomment to run immediately (useful for Node.js testing)
// testAllEndpoints();
