# 🚀 Ultimate Node.js & Express.js Interview Master Sheet
> **Note for Interviews:** Yeh document aapki 120 slides ke gaps ko 100% fill karta hai. Isme deep-down architecture, event loop internals, production security attacks, advanced middlewares, streams, auth lifecycle, aur tricky interview output questions complete detail mein covered hain.

---

## 📑 Index of Modules
1. [What is Already in Your 120 Slides (Quick Summary)](#1-what-is-already-in-your-120-slides)
2. [Node.js Deep Architecture & Program Execution Journey](#2-nodejs-deep-architecture--program-execution-journey)
3. [Event Loop & Libuv 6 Phases Deep Dive](#3-event-loop--libuv-6-phases-deep-dive)
4. [Buffers, Streams & Memory Management](#4-buffers-streams--memory-management)
5. [Concurrency, Multithreading & Scaling (Cluster, Worker Threads, Child Process)](#5-concurrency-multithreading--scaling)
6. [Modern Node.js (ESM, Crypto, Native Env, Process Lifecycle)](#6-modern-nodejs-features--system-utilities)
7. [Advanced Express.js Middleware Patterns & Architecture](#7-advanced-expressjs-middleware-patterns)
8. [Complete Security Vulnerabilities, Attacks & Production Hardening](#8-security-attacks-vulnerabilities--production-hardening)
9. [Request Validation & File Uploads (Zod & Multer)](#9-request-validation--file-uploads)
10. [Complete Authentication & Authorization Lifecycle (JWT Access + Refresh Rotation, RBAC)](#10-authentication--authorization-architecture)
11. [Production Centralized Error Handling & Graceful Shutdown](#11-production-error-handling--resilience)
12. [Real-Time WebSockets & Performance Optimization](#12-real-time-websockets--performance-optimization)
13. [Top 10 Tricky Output-Based Interview Questions & Solutions](#13-top-10-tricky-interview-output-questions)

---

## 1. What is Already in Your 120 Slides
Aapki slides mein ye topics standard cover hain:
- Node.js runtime definition, JS in browser vs Node.js.
- Sync vs Async, Single-threaded concept, basic Event Emitter.
- CommonJS (`require`, `module.exports`, `exports`), basic `fs`, `path`, `os`, `http.createServer()`.
- Express basics, simple routing, `app.use()`, basic 5 middleware types, EJS templates.
- REST API definition, HTTP verbs (GET, POST, PUT, PATCH, DELETE), Status codes, CORS basics, API versioning.
- Basic Password hashing with `bcrypt` & salt, Basic Auth, API Key, JWT token 3 parts (`header.payload.signature`).
- `try-catch`, error-first callback, `.catch()`, async/await, basic error middleware.

---

## 2. Node.js Deep Architecture & Program Execution Journey

Jab aap terminal mein command chalate hain: `node app.js`, deep-down yeh 5 steps hote hain:

```
  [ node app.js ]
         │
         ▼
 1. C++ BOOTSTRAP (V8 Heap & Stack Allocation + Libuv Instance + 4 Worker Threads spawned)
         │
         ▼
 2. MODULE WRAPPER (File wrapped into IIFE: exports, require, module, __filename, __dirname)
         │
         ▼
 3. TOP-LEVEL SYNC CODE (Line-by-line execution on V8 Call Stack)
    ├─ Network/Sockets ──► Delegated to OS Kernel (epoll on Linux / IOCP on Windows)
    ├─ File/Crypto/DNS  ──► Delegated to Libuv Thread Pool (4 background threads)
    └─ Timers           ──► Registered in Libuv Min-Heap Tree
         │
         ▼
 4. MICROTASKS CHECK (Call stack empty hote hi: 1. process.nextTick ➡️ 2. Promises)
         │
         ▼
 5. EVENT LOOP CYCLES (Timers ➡️ Pending ➡️ Idle ➡️ Poll ➡️ Check ➡️ Close)
         │ (Active handles count == 0?)
         ▼
 6. PROCESS TERMINATION (Emit 'beforeExit' ➡️ 'exit' ➡️ Terminate with Exit Code 0)
```

### Key Interview Points:
1. **Module Wrapper Function:** Har file execute hone se pehle is wrapper function ke andar wrap hoti hai:
   ```javascript
   (function (exports, require, module, __filename, __dirname) {
       // Your actual code
   });
   ```
2. **Single-Threaded vs Multi-Threaded reality:**
   - **V8 JavaScript Execution:** 100% Single-Threaded (One Call Stack).
   - **Node.js Process:** Multi-Threaded (Libuv background thread pool, garbage collection threads, OS asynchronous kernel threads).
3. **OS Kernel vs Libuv Thread Pool:**
   - **Network I/O:** Thread pool use **nahi** karta. Direct OS non-blocking primitives use karta hai (*Linux: `epoll`, Windows: `IOCP`, Mac: `kqueue`*).
   - **File I/O (`fs`), Crypto (`pbkdf2`, `bcrypt`), DNS Lookup (`dns.lookup`), Compression (`zlib`):** Libuv **Thread Pool** (default 4 threads) use karte hain.

---

## 3. Event Loop & Libuv 6 Phases Deep Dive

Libuv Event loop ek continuous cycle mein 6 phases mein kaam karta hai:

```
   ┌───────────────────────────────────────────┐
┌─►│ 1. TIMERS (setTimeout, setInterval)       │
│  └─────────────────────┬─────────────────────┘
│  ┌─────────────────────┴─────────────────────┐
│  │ 2. PENDING CALLBACKS (I/O system errors)  │
│  └─────────────────────┬─────────────────────┘
│  ┌─────────────────────┴─────────────────────┐
│  │ 3. IDLE / PREPARE (Internal Libuv housekeeping)│
│  └─────────────────────┬─────────────────────┘
│  ┌─────────────────────┴─────────────────────┐
│  │ 4. POLL (Retrieve new I/O events, wait)   │
│  └─────────────────────┬─────────────────────┘
│  ┌─────────────────────┴─────────────────────┐
│  │ 5. CHECK (setImmediate callbacks)         │
│  └─────────────────────┬─────────────────────┘
│  ┌─────────────────────┴─────────────────────┐
│  │ 6. CLOSE CALLBACKS (socket.on('close'))   │
└──┴───────────────────────────────────────────┘
```

### Microtasks VIP Lane (Crucial Rule):
> **Rule:** Call stack khali hone ke baad aur Event Loop ke **har single phase ke transition ke beech**, Node.js pehle **Microtask Queue** ko poora empty karta hai:
> 1. `process.nextTick` Queue (Highest Priority)
> 2. `Promise` Microtask Queue (`.then()`, `await` continuations)

### `setImmediate()` vs `setTimeout(fn, 0)`:
- `setImmediate()`: **Check Phase** mein run hota hai (Poll phase ke turant baad).
- `setTimeout(fn, 0)`: **Timers Phase** mein run hota hai.
- **Inside an I/O cycle (e.g. `fs.readFile`):** `setImmediate` hamesha `setTimeout(0)` se **pehle** run hoga kyunki `fs` Poll phase mein complete hota hai aur agla phase Check hota hai.

### Libuv Thread Pool Size:
Default thread pool size 4 hota hai. Isko change karne ke liye environment variable use hota hai:
```bash
UV_THREADPOOL_SIZE=8 node app.js
```

---

## 4. Buffers, Streams & Memory Management

### A. Buffers (Short Explanation + All Methods)
- **🔹 Buffer Kya Hai? (1 Line):** `Buffer = Binary data (bytes) ka fixed-size container`. Files, images, videos, network data ke liye use hota hai.
- **🔹 Kyun chahiye?** JavaScript strings samajhti hai, lekin raw hardware binary bytes (0x00-0xFF) handle karne ke liye Buffer zaroori hai.

#### 📌 Complete Buffer Methods Matrix:
| Category | Method / Syntax | Description / Role | Example Output |
| :--- | :--- | :--- | :--- |
| **CREATION** | `Buffer.from('Hi')` | String se buffer banao | `<Buffer 48 69>` |
| **CREATION** | `Buffer.from([72, 105])` | Byte array se buffer banao | `<Buffer 48 69>` |
| **CREATION** | `Buffer.alloc(5)` | 5 bytes (zero-filled, Safe) | `<Buffer 00 00 00 00 00>` |
| **CREATION** | `Buffer.allocUnsafe(5)` | Fast but uncleaned memory (Unsafe) | `<Buffer 8a 3f ...>` |
| **CREATION** | `Buffer.concat([a, b])` | Multiple buffers ko jodo | `<Buffer ...>` |
| **READ** | `buf.toString('utf8')` | String mein convert (or 'hex' / 'base64') | `'Hello'` |
| **READ** | `buf[0]` & `buf.length` | Byte padho & total length check karo | `72` & `5` |
| **READ** | `buf.slice(0, 2)` | Buffer ka sub-portion nikaalo | `<Buffer 48 65>` |
| **WRITE** | `buf.write('Hello')` | Buffer mein string write karo | `5` (bytes written) |
| **WRITE** | `buf[0] = 72` / `buf.fill(0)` | Single byte set karo / zero fill karo | Updates RAM bytes |
| **COMPARE** | `buf.equals(other)` | Exact same bytes check (true/false) | `true` |
| **COMPARE** | `Buffer.compare(a, b)` | Binary comparison sort order | `-1`, `0`, `1` |
| **CHECK** | `Buffer.isBuffer(x)` | Check if object is a Buffer instance | `true` / `false` |
| **CHECK** | `Buffer.byteLength('Hi')` | String ka actual byte size nikaalo | `2` |

```javascript
// ===== 1. CREATE =====
Buffer.from('Hello');           // <Buffer 48 65 6c 6c 6f>
Buffer.from([72, 101, 108]);    // <Buffer 48 65 6c>
Buffer.alloc(3);                // <Buffer 00 00 00>
Buffer.concat([Buffer.from('Hi '), Buffer.from('there')]); // 'Hi there'

// ===== 2. READ =====
const buf = Buffer.from('Hello');
buf.toString();                 // 'Hello'
buf.toString('hex');            // '48656c6c6f'
buf.toString('base64');         // 'SGVsbG8='
buf[0];                         // 72
buf.length;                     // 5
buf.slice(0, 2).toString();     // 'He'

// ===== 3. WRITE =====
const b = Buffer.alloc(5);
b.write('Hi');                  // b = 'Hi'
b[0] = 72;                      // 'H'
b.fill(0);                      // all zeros

// ===== 4. COMPARE / CHECK =====
Buffer.from('abc').equals(Buffer.from('abc'));       // true
Buffer.compare(Buffer.from('a'), Buffer.from('b'));  // -1
Buffer.isBuffer(buf);                                // true
Buffer.byteLength('Hello');                          // 5
```

### B. Node.js Streams & 4 Core Types (English Master Guide)
- **Definition:** A Stream is an abstract interface for processing continuous streaming data chunk-by-chunk (default 64KB per chunk) without loading the entire payload into RAM at once.
- **Why Streams?** Reading a 2GB video file via `fs.readFileSync` consumes 2GB of RAM and crashes under high traffic. Using `fs.createReadStream` consumes only **~64KB of RAM** per chunk regardless of total file size.

#### 📌 Buffer vs Stream Comparison:
| Feature / Metric | Buffer (Without Streams) | Streams (With Node.js) | Enterprise Advantage |
| :--- | :--- | :--- | :--- |
| **Memory Allocation** | Loads entire file into RAM at once | Processes data in sequential 64KB chunks | Zero Out-Of-Memory (OOM) crashes |
| **2GB Video File RAM** | Consumes 2GB RAM per request | Consumes only ~64KB RAM | Scales to 10,000+ concurrent requests |
| **Time to First Byte (TTFB)** | Slow (waits for full disk read) | Instant playback (YouTube streaming model) | Ultra-low latency |
| **Best For** | Small tokens, hashes, auth headers | Large files, Media streaming, Network sockets | Maximum server throughput |

#### 📌 4 Types of Streams:
```
┌──────────────────────────────────────────────────────────┐
│  1. Readable   →  Data Source (fs.createReadStream, req) │
│  2. Writable   →  Data Sink   (fs.createWriteStream, res)│
│  3. Duplex     →  Bidirectional Read + Write (net.Socket)│
│  4. Transform  →  Modify data in-flight (zlib.createGzip)│
└──────────────────────────────────────────────────────────┘
```

#### 📌 Stream Lifecycle Events:
| Event | Trigger Condition |
| :--- | :--- |
| `data` | Emitted when a new chunk of data is ready to be read (Readable) |
| `end` | Emitted when no more data is available to read (Readable) |
| `finish` | Emitted when all data has been completely flushed to the underlying system (Writable) |
| `drain` | Emitted when the internal write buffer becomes empty after being saturated (Writable) |
| `error` | Emitted when an I/O error or stream processing error occurs |
| `close` | Emitted when the underlying resource (e.g. file descriptor or socket) has been closed |

---

### C. What is Backpressure & How Does Flow Control Work?

#### 1. The Core Problem:
Backpressure occurs when the **Producer (Readable Stream)** generates data faster than the **Consumer (Writable Stream)** can write to disk or transmit over a network connection.

#### 2. The Internal Buffer (`highWaterMark`):
- Every stream has an internal buffer threshold called `highWaterMark` (default: **64KB** for file streams, **16KB** for standard object streams).
- When a writer's buffer fills up to `highWaterMark`, `writeStream.write(chunk)` returns `false`.

#### 3. Flow Control Mechanism:
1. When `write()` returns `false`, the application must call `readStream.pause()` to stop reading from the source.
2. Once the consumer flushes its internal buffer, it emits the **`'drain'`** event.
3. The application listens for `'drain'` and calls `readStream.resume()` to continue reading data.

```javascript
// Manual Backpressure Implementation:
const readStream = fs.createReadStream('source-video.mp4');
const writeStream = fs.createWriteStream('dest-video.mp4');

readStream.on('data', (chunk) => {
  const canContinue = writeStream.write(chunk);
  if (!canContinue) {
    // Backpressure detected: Write buffer is saturated
    readStream.pause();
  }
});

writeStream.on('drain', () => {
  // Write buffer drained: Resume reading data chunks
  readStream.resume();
});
```

#### 4. `pipe()` vs Modern `pipeline()`:
- `readStream.pipe(writeStream)` automatically handles `pause()` and `resume()` backpressure under the hood.
- **Limitation of `pipe()`:** Does NOT automatically destroy and clean up streams if an error occurs mid-transfer, leading to memory/file descriptor leaks.
- **Production Standard:** Use `stream.pipeline()` or `stream/promises` because it guarantees automatic stream destruction, proper backpressure control, and unified error handling:

```javascript
const { pipeline } = require('stream/promises');
const fs = require('fs');
const zlib = require('zlib');

async function processBigFile() {
  try {
    await pipeline(
      fs.createReadStream('input.csv'),
      zlib.createGzip(),
      fs.createWriteStream('input.csv.gz')
    );
    console.log('Stream pipeline completed safely with 0 memory leaks!');
  } catch (err) {
    console.error('Pipeline failed and auto-cleaned all resources:', err);
  }
}
```

---

## 5. Concurrency, Multithreading & Scaling

Node.js single-threaded hote hue bhi in 3 tareeqon se scale hota hai:

### 1. Cluster Module (Multi-Core CPU Scaling)
Master process server ke har CPU core ke liye ek Worker process fork karta hai:
```javascript
const cluster = require('cluster');
const http = require('http');
const os = require('os');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  console.log(`Primary ${process.pid} is running. Forking ${numCPUs} workers...`);
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  cluster.on('exit', (worker) => {
    console.log(`Worker ${worker.process.pid} died. Spawning replacement...`);
    cluster.fork();
  });
} else {
  // Workers share the same TCP port
  http.createServer((req, res) => res.end('Handled by worker ' + process.pid)).listen(8000);
}
```

### 2. Worker Threads (`worker_threads`)
CPU-intensive tasks (Image processing, complex math, heavy crypto) ke liye main thread ko freeze kiye bina threads banana:
```javascript
// main.js
const { Worker } = require('worker_threads');

function runService(workerData) {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./worker.js', { workerData });
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
    });
  });
}
```

### 3. Child Processes (`child_process`)
System shell commands run karne ke 4 methods:
- `exec()`: Buffer mein pura output store karta hai (small output ke liye).
- `spawn()`: Streams ke through continuous large output handle karta hai.
- `execFile()`: Bina shell invoke kiye executable direct run karta hai (Secure).
- `fork()`: Node.js process fork karta hai jisme built-in IPC (Inter-Process Communication) channel hota hai (`process.send()`, `process.on('message')`).

---

## 6. Modern Node.js Features & System Utilities

### A. ES Modules (ESM) vs CommonJS (CJS)
- **CommonJS:** Synchronous `require()`, dynamic loading, default in older Node.
- **ES Modules:** Asynchronous `import`/`export`, static analysis, `"type": "module"` in `package.json`.
- **`__dirname` & `__filename` in ESM:**
  ```javascript
  import { fileURLToPath } from 'url';
  import { dirname } from 'path';

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);
  ```

### B. Built-in `crypto` Module
```javascript
const crypto = require('crypto');

// 1. UUID generation
const id = crypto.randomUUID();

// 2. SHA-256 Hashing
const hash = crypto.createHash('sha256').update('password123').digest('hex');

// 3. HMAC (Keyed Hashing)
const hmac = crypto.createHmac('sha256', 'secret_key').update('data').digest('hex');
```

### C. Native `.env` File (Node v20+)
Bina `dotenv` package ke command line flag se `.env` load karna:
```bash
node --env-file=.env server.js
```

---

## 7. Advanced Express.js Middleware Patterns & Master Directory

### 📌 Top 14 Third-Party Middlewares Master Table:
| Middleware | Kya Karti Hai? (Role) | Kyun Use Karein? (Benefit) | Kab Use Karein? (When) |
| :--- | :--- | :--- | :--- |
| **Helmet** | HTTP security headers set karti hai (CSP, X-Frame-Options) | Hackers se protect karta hai — clickjacking, XSS, sniffing attacks rokta hai | Har production app mein |
| **CORS** | Cross-origin requests allow karta hai | Frontend (`localhost:3000`) se backend (`localhost:5000`) ko call karne deta hai | Jab frontend aur backend alag domain/port ho |
| **Morgan** | HTTP requests ka structured log rakhti hai | Debugging & monitoring easy — method, URL, status & response time | Development + Production dono mein |
| **Multer** | File uploads handle karti hai (`multipart/form-data`) | User avatar, images, documents upload karne ke liye | Jab file upload feature ho |
| **Cookie-Parser** | Browser ki cookies parse karti hai (`req.cookies`) | Auth tokens, session IDs, user preferences read karne ke liye | Jab cookie-based login/session ho |
| **express.json()** | Request body (JSON / URL-encoded) parse karti hai | POST/PUT request ka payload `req.body` mein accessible hota hai | Har POST/PUT/PATCH API route mein |
| **Passport** | Authentication handle karti hai (JWT, OAuth, Local) | Login, signup, Google/GitHub OAuth login standard banata hai | Jab social login ya user auth chahiye |
| **express-session** | Server-side session manage karti hai | User logged-in rehta hai multiple requests ke beech (Stateful auth) | Jab session-based auth ho |
| **Zod / express-validator** | Input payload schema validation karti hai | Malicious / invalid payload reject karti hai controller se pehle | Har user input endpoint par |
| **compression** | HTTP responses ko Gzip/Deflate se compress karti hai | Network payload size kam hota hai, API loading speed badhti hai | Production mein performance ke liye |
| **express-rate-limit** | Requests limit karti hai per IP address | DDoS attacks, API abuse aur brute-force password guessing rokta hai | Har public API route par |
| **Winston** | Enterprise structured JSON logging | Log levels (info/error/warn), file transports & production monitoring | Production microservices mein |
| **dotenv** | `.env` file se environment variables load karti hai | Secrets (API keys, DB credentials) code repo se alag rakhne ke liye | Har project mein |
| **nodemon** | File change detect karke auto-restart karta hai | Development mein baar-baar manual restart nahi karna padta | Development environment only |

### A. Configurable Middleware (Factory Functions / Closures)
```javascript
const restrictTo = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ success: false, message: 'You do not have permission!' });
    }
    next();
  };
};

// Usage:
app.delete('/api/users/:id', authMiddleware, restrictTo('admin', 'superadmin'), deleteUser);
```

### B. `next()` Control Flow Variants
- `next()`: Agle matching middleware/route handler pe jata hai.
- `next('route')`: Current route pipeline ke baaki middlewares skip karke **agle route definition** pe jump karta hai (sirf `app.METHOD()` ya `router.METHOD()` mein valid).
- `next(err)`: Sabhi regular middlewares ko skip karke seedhe **Global Error Handler** (`(err, req, res, next)`) pe jump karta hai.

### C. Async Wrapper (`asyncHandler`)
```javascript
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Controller without try/catch:
const getUser = asyncHandler(async (req, res) => {
  const user = await UserService.findById(req.params.id);
  res.status(200).json({ success: true, data: user });
});
```

---

## 8. Security Attacks, Vulnerabilities & Production Hardening

| Attack / Exploit | Threat Description | Production Defense & Code |
| :--- | :--- | :--- |
| **1. ReDoS (Regex Denial of Service)** | Complex regex mein catastrophic backtracking ki wajah se Event Loop 100% hang ho jata hai. | Safe regex patterns use karein, `safe-regex` validator, aur input length limits lagayein. |
| **2. Payload Bomb (Body DOS)** | Attacker 50MB ka heavy JSON bhej kar server RAM crash karta hai. | `app.use(express.json({ limit: '10kb' }));` |
| **3. Command Injection** | User input `child_process.exec()` mein pass karne se hacker OS commands run karta hai. | `exec()` avoid karein. Hamesha `execFile()` ya `spawn()` with arguments array use karein. |
| **4. Path Traversal** | `../../etc/passwd` query pass karke server ki system files read karna. | `path.normalize()` use karein aur verify karein ki path allowed base directory ke andar ho. |
| **5. Prototype Pollution** | Object recursive merge ke dauran `__proto__` mutate karke app logic todna. | `Object.create(null)` use karein, `Object.freeze()`. |
| **6. XSS & Token Theft** | Malicious script se `localStorage` ka JWT chori karna. | `helmet()` Content-Security-Policy lagayein aur JWT Refresh Token ko **`httpOnly; Secure; SameSite=Strict`** cookie mein rakhein. |
| **7. HTTP Parameter Pollution (HPP)** | Query params duplicate bhej kar (`?role=user&role=admin`) auth bypass karna. | `const hpp = require('hpp'); app.use(hpp());` |
| **8. Rate Limiting / DDoS** | Brute force login attempts aur API spamming. | `express-rate-limit` middleware lagayein (e.g. 5 attempts / 15 mins). |
| **9. JWT `alg: "none"` Exploit** | Token header mein algorithm `none` bhej kar bina signature verify kiye login karna. | `jwt.verify(token, secret, { algorithms: ['HS256'] })` strictly define karein. |
| **10. Information Fingerprinting** | `X-Powered-By: Express` header se attacker ko stack version leak hona. | `app.disable('x-powered-by');` aur `helmet()` use karein. |

---

## 9. Request Validation & File Uploads

### A. Input Validation with Zod
```javascript
const { z } = require('zod');

const registerSchema = z.object({
  body: z.object({
    email: z.string().email("Invalid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    age: z.number().min(18).optional()
  })
});

const validate = (schema) => (req, res, next) => {
  try {
    schema.parse({ body: req.body, query: req.query, params: req.params });
    next();
  } catch (err) {
    return res.status(400).json({ success: false, errors: err.errors });
  }
};

app.post('/api/register', validate(registerSchema), registerController);
```

### B. Multer File Upload Middleware
```javascript
const multer = require('multer');
const path = require('path');

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, 'uploads/'),
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const fileFilter = (req, file, cb) => {
  if (file.mimetype.startsWith('image/')) cb(null, true);
  else cb(new Error('Only images are allowed!'), false);
};

const upload = multer({ storage, limits: { fileSize: 2 * 1024 * 1024 }, fileFilter }); // 2MB limit
```

---

## 10. Authentication & Authorization Architecture

### A. Complete Access Token + Refresh Token Rotation Flow
1. **Login:**
   - **Access Token:** Short-lived (15 minutes), payload mein `userId` & `role`. Client ko JSON mein send hota hai.
   - **Refresh Token:** Long-lived (7 days), random secure string ya signed JWT. **`httpOnly; Secure; SameSite=Strict`** cookie mein save hota hai.
2. **Access Token Expiry (401 Response):**
   - Client silent request bhejta hai `/api/v1/auth/refresh-token`.
3. **Token Rotation:**
   - Server cookie se Refresh token read karta hai, verify karta hai, aur **naya Access Token + naya Refresh Token** issue karta hai (Purana refresh token blacklist/delete hota hai).

### B. JWT Verification Middleware
```javascript
const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, message: 'Unauthorized: No token provided' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, process.env.JWT_ACCESS_SECRET);
    req.user = decoded; // { id, role }
    next();
  } catch (err) {
    return res.status(401).json({ success: false, message: 'Invalid or Expired Token' });
  }
};
```

---

## 11. Production Error Handling & Resilience

### A. Custom `ApiError` Class
```javascript
class ApiError extends Error {
  constructor(statusCode, message, isOperational = true, stack = '') {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    if (stack) this.stack = stack;
    else Error.captureStackTrace(this, this.constructor);
  }
}
```

### B. Global Centralized Error Middleware
```javascript
// 1. 404 Route Catch-All (Place after all routes)
app.use((req, res, next) => {
  next(new ApiError(404, `Route ${req.originalUrl} not found`));
});

// 2. Global Error Handler (Place at the absolute end)
app.use((err, req, res, next) => {
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    success: false,
    message: err.message || 'Internal Server Error',
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});
```

### C. Graceful Shutdown
```javascript
const server = app.listen(PORT);

const shutdown = (signal) => {
  console.log(`${signal} received. Closing HTTP server gracefully...`);
  server.close(() => {
    console.log('HTTP server closed. Exiting process...');
    process.exit(0);
  });
  // Force close after 10s if hanging
  setTimeout(() => process.exit(1), 10000);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
process.on('unhandledRejection', (err) => {
  console.error('UNHANDLED REJECTION:', err);
  shutdown('unhandledRejection');
});
```

---

## 12. Real-Time WebSockets & Performance Optimization

### A. Socket.IO with Express
```javascript
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);
  socket.on('join_room', (room) => socket.join(room));
  socket.on('send_message', (data) => {
    socket.to(data.room).emit('receive_message', data);
  });
  socket.on('disconnect', () => console.log('User disconnected'));
});

server.listen(3000);
```

### B. Response Compression Middleware
```javascript
const compression = require('compression');
app.use(compression()); // Gzip/Brotli payload compression
```

---

## 13. Top 10 Tricky Interview Output Questions

#### ❓ Q1: Event Loop Execution Order
```javascript
console.log("1");
setTimeout(() => console.log("2"), 0);
setImmediate(() => console.log("3"));
process.nextTick(() => console.log("4"));
Promise.resolve().then(() => console.log("5"));
console.log("6");
```
**Output:** `1 -> 6 -> 4 -> 5 -> 2 -> 3` (Note: Timers vs Immediate top-level can depend on OS tick, but `nextTick` always precedes `Promise`, which precedes timers/immediate).

---

#### ❓ Q2: Execution Order inside I/O (`fs.readFile`)
```javascript
const fs = require('fs');
fs.readFile(__filename, () => {
    setTimeout(() => console.log('Timeout'), 0);
    setImmediate(() => console.log('Immediate'));
});
```
**Output:** `Immediate -> Timeout`
**Why?** `fs.readFile` callback executes in the **Poll Phase**. After Poll phase comes the **Check Phase** (`setImmediate`), before the loop loops back to Timers.

---

#### ❓ Q3: Double `next()` Bug
```javascript
app.use((req, res, next) => {
  if (!req.headers.token) {
    res.status(401).send("No Token");
  }
  next();
});
```
**Output / Error:** `Error [ERR_HTTP_HEADERS_SENT]: Cannot set headers after they are sent to the client.`
**Fix:** Hamesha `return next();` ya `return res.status(...)...` likhein.

---

#### ❓ Q4: What happens if you call `process.nextTick()` recursively?
```javascript
function recursive() {
  process.nextTick(recursive);
}
recursive();
```
**Answer:** It completely **starves the Event Loop**. Node.js microtask queue kabhi empty nahi hogi aur I/O, Timers, ya HTTP requests kabhi execute nahi ho payenge.

---

#### ❓ Q5: Difference between `Buffer.alloc()` and `Buffer.allocUnsafe()`
- `Buffer.alloc(size)`: Memory allocate karta hai aur zero se fill karta hai (Safe).
- `Buffer.allocUnsafe(size)`: Memory allocate karta hai bina purana data clean kiye. Fast hota hai lekin sensitive data leak hone ka risk hota hai.

---

### 🏁 Final Advice for Your Interview
Agar aap is Master Sheet ke:
1. **Event Loop 6 phases + Microtasks execution order**
2. **Streams (`pipeline`) & Buffers**
3. **Cluster vs Worker Threads vs Child Process**
4. **Security Attacks (ReDoS, Body DOS, XSS vs CSRF, Token Theft, HPP)**
5. **JWT Refresh Rotation in httpOnly cookie + RBAC**
6. **Centralized Error Handling (`asyncHandler` + `ApiError`)**

...itne topics thoroughly samajh lete hain, toh aap kisi bhi Senior/Lead level Node.js backend interview ko confidently crack kar sakte hain!
