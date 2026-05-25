import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';
import { htmlReport } from 'https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';

export const options = {
  stages: [
    { duration: '10s', target: 5   },   // warm up to 5 VUs
    { duration: '5s',  target: 100 },   // sudden spike to 100 VUs
    { duration: '30s', target: 100 },   // hold the spike
    { duration: '10s', target: 5   },   // drop back to baseline
    { duration: '30s', target: 5   },   // observe recovery
  ],
  thresholds: {
    http_req_duration: ['p(95)<800'],
    http_req_failed:   ['rate<0.02'],
    http_req_waiting:  ['p(95)<600'],
  },
};

const tasks = [
  'Fix login bug breaking production',
  'Patch security vulnerability in auth module',
  'Resolve database crash on staging server',
  'Emergency hotfix for checkout flow',
  'Critical server downtime needs attention now',
  'Submit final report by end of day',
  'Prepare slides for team meeting next week',
  'Schedule one on one with manager',
  'Update project timeline in spreadsheet',
  'Review pull requests from teammates',
  'Plan onboarding for new hire starting Monday',
  'Send weekly status update email to team',
  'Read latest issue of tech magazine',
  'Watch new episode of favourite series tonight',
  'Browse vacation destinations online for fun',
  'Listen to podcast on long commute',
  'Read fiction book before bed',
  'Watch documentary about deep space exploration',
  'Browse new restaurants in the neighbourhood',
  'Read article about machine learning trends',
];

const URL = 'http://localhost:5001/predict';
const HEADERS = { 'Content-Type': 'application/json' };

export default function () {
  const payload = JSON.stringify({ task: randomItem(tasks) });
  const res = http.post(URL, payload, { headers: HEADERS });

  check(res, {
    'status is 200':      (r) => r.status === 200,
    'has priority field': (r) => {
      try { return r.json('priority') !== undefined; }
      catch (e) { return false; }
    },
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'k6_report_spike.html': htmlReport(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
