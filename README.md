# ⚡ Node.js & Express.js Master Revision Deck & Interview Guide

Complete, high-yield **Node.js & Express.js Master Revision Deck** containing sequential slide images, interactive web-based slide deck viewer, and exhaustive interview preparation guides.

---

## 🌟 What's Inside

1. **`slide_revision_deck.html`**:
   - Interactive presentation deck with keyboard navigation (⬅ / ➡ Arrow Keys, Spacebar), fullscreen mode, and live topic search.
   - Exact high-contrast slide theme: Solid black header bar (`#000000`) with vibrant yellow keywords (`#FFE600`), red underline, crisp typography, golden diamond bullets (`❖`), and dark VS Code editor boxes.
2. **`ultimate_nodejs_express_interview_master_guide.md`**:
   - Exhaustive 13-Module text guide covering deep internals, security attacks, token rotation, and performance.
3. **`nodejs_express_complete_slide_wise_master_deck.md`**:
   - Chronological slide-by-slide Q&A revision notes.
4. **`stream_all_in_one_demo.js`**:
   - Single runnable Node.js program demonstrating **all 4 Stream types** (Readable, Transform, Duplex, Writable) with backpressure handling.
5. **Slide Decks (`nodejs_slides_complete/`, `nodejs_slides/`, etc.)**:
   - 120+ sequential slide graphics covering end-to-end Node.js and Express.js core curriculum.

---

## 📑 Curriculum & Topics Covered

- **Module 1: Node.js Internals & Architecture**
  - V8 Engine (Ignition Interpreter + TurboFan JIT Optimizer)
  - Libuv Thread Pool (4 Workers: fs, crypto, dns, zlib)
  - OS Kernel Non-Blocking I/O (epoll / kqueue / IOCP with 0 Threads blocked)
  - Event Loop 6 Phases & Microtasks VIP Priority (`process.nextTick` vs Promises)
  - Concurrency: `worker_threads` vs `cluster` vs `child_process`
- **Module 2: Modules & Execution**
  - CommonJS (`require()`, `module.exports`) vs ES Modules (`import`/`export`, `.mjs`, top-level await)
  - Node.js Module Wrapper Function IIFE
- **Module 3: Buffers, Streams & Memory Management**
  - Buffers: Raw C++ Binary Memory allocation, all core methods (`from`, `alloc`, `allocUnsafe`, `toString`, `concat`, `equals`)
  - Streams: 4 Types (`Readable`, `Writable`, `Duplex`, `Transform`), Stream Events, Backpressure & Flow Control, `pipe()` vs `pipeline()`
- **Module 4 & 5: Express.js Architecture & Middlewares**
  - Request-Response pipeline, App vs Route middleware, Error middleware
  - **Top 14 Third-Party Middlewares Master Matrix** (`Helmet`, `CORS`, `Morgan`, `Multer`, `Cookie-Parser`, `express-rate-limit`, `Winston`, etc.)
- **Module 6 & 7: Routing & Templates**
  - `express.Router()`, route chaining, nested routing, EJS templating
- **Module 8: Request Validation & Uploads**
  - Zod Schema Validation, Multer multipart upload security & MIME type filtering
- **Module 9: REST APIs & Protocols**
  - HTTP Verbs, Idempotence, Status codes, CORS, Serialization, API versioning
- **Module 10: Security Attacks & Hardening**
  - ReDoS, Prototype Pollution, Parameter Pollution (`hpp`), Rate limiting, Helmet security headers
- **Module 11: Enterprise Authentication & Authorization**
  - Password hashing (`bcrypt`), JWT Tokens, Refresh Token Rotation, HttpOnly Cookie security, Role-Based Access Control (RBAC)
- **Module 12: Enterprise Error Architecture**
  - Operational vs Programmer errors, Custom `AppError` class, Centralized error middleware, Process exception safety

---

## 🚀 Getting Started

### 1. Run Interactive Slide Deck:
Simply open **`slide_revision_deck.html`** in any web browser:
- **`Left / Right Arrow` or `Spacebar`**: Navigate slides
- **`Sidebar Search`**: Search any topic instantly
- **`Fullscreen`**: Click `⛶ Fullscreen` for presentation mode

### 2. Run Streams Demo:
```bash
node stream_all_in_one_demo.js
```

---

## 👨‍💻 Author & Repository
- **Author:** [shivtyagidev](https://github.com/shivtyagidev)
- **Repository:** [https://github.com/shivtyagidev/node_js-_slides](https://github.com/shivtyagidev/node_js-_slides)
