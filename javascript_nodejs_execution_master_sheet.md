# ⚡ The Ultimate JavaScript & Node.js Runtime & Execution Master Sheet

> **One-Shot Revision Guide & Complete Missing Slides Curriculum:** Pointwise architectural reference covering Core JavaScript (V8 Engine), Node.js Runtime (Libuv & OS Kernel), and **All 68 Missing Slides (Slides 125 to 192)** with high-clarity diagrams, code examples, and interview Q&A.

---

## 🗺️ Master End-to-End Execution Flow Diagram

```
+-------------------------------------------------------------------------------------------------------+
|                                    1. OPERATING SYSTEM & PROCESS BOOT                                 |
|          Node.js Process (node.exe) ──► Allocates V8 Isolate + Libuv Instance + 4 Thread Pool         |
+-------------------------------------------------------------------------------------------------------+
                                                   │
                                                   ▼
+-------------------------------------------------------------------------------------------------------+
|                                 2. MODULE WRAPPER & V8 JIT COMPILATION                                |
|                                                                                                       |
|   Source Code ──► Module Wrapper IIFE ──► Scanner (Tokens) ──► Parser ──► AST (Syntax Tree)           |
|                                                                                │                      |
|                                                                                ▼                      |
|                                                                     Ignition Interpreter              |
|                                                                                │                      |
|                                                                 (Bytecode Execution + Profiler)       |
|                                                                                │                      |
|                                                                     TurboFan JIT Compiler             |
|                                                                                │                      |
|                                                                     Native Machine Code (0101)        |
+-------------------------------------------------------------------------------------------------------+
                                                   │
                                                   ▼
+-------------------------------------------------------------------------------------------------------+
|                                    3. MEMORY ALLOCATION (RAM)                                         |
|                                                                                                       |
|       CALL STACK (LIFO Execution)                    MEMORY HEAP (Dynamic Storage)                    |
|    ┌─────────────────────────────────┐           ┌───────────────────────────────────────────────┐    |
|    │ [Function Execution Context]    │           │ New Space (Nursery / Intermediate - Scavenge) │    |
|    ├─────────────────────────────────┤           │ Old Space (Tenured Generation - Mark-Sweep)   │    |
|    │ [Global Execution Context]      │ ──Pointers──► Large Object Space & Map Space (Shapes)     │    |
|    └─────────────────────────────────┘           └───────────────────────────────────────────────┘    |
+-------------------------------------------------------------------------------------------------------+
                                                   │
                          ┌────────────────────────┴────────────────────────┐
                          ▼                                                 ▼
             [ 4. SYNCHRONOUS CODE ]                               [ 5. ASYNC DELEGATION ]
             Executes line-by-line                                 Offloaded to OS Kernel / Libuv
             on the Call Stack                                              │
                                                                            ▼
+-------------------------------------------------------------------------------------------------------+
|                                  6. LIBUV RUNTIME & CONCURRENCY PATHS                                 |
|                                                                                                       |
|     Path A: Non-Blocking OS Kernel (0 Threads)         Path B: Libuv Thread Pool (4 Workers)         |
|     (Network, HTTP, TCP Sockets: epoll/IOCP)           (File System 'fs', Crypto, DNS, zlib)          |
+-------------------------------------------------------------------------------------------------------+
                                                   │ Completed callbacks
                                                   ▼
+-------------------------------------------------------------------------------------------------------+
|                                 7. QUEUES & THE 6-PHASE EVENT LOOP                                    |
|                                                                                                       |
|    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐    |
|    │ VIP MICROTASKS (Drained between phases): 1. process.nextTick ──► 2. Promise Microtasks      │    |
|    └──────────────────────────────────────────────┬──────────────────────────────────────────────┘    |
|                                                   ▼                                                   |
|    ┌─────────────────────────────────────────────────────────────────────────────────────────────┐    |
|    │ PHASE 1: Timers (setTimeout, setInterval)                                                   │    |
|    │ PHASE 2: Pending Callbacks (Deferred I/O errors)                                            │    |
|    │ PHASE 3: Idle, Prepare (Internal Libuv use)                                                 │    |
|    │ PHASE 4: Poll (epoll/IOCP wait & execute I/O callbacks)                                      │    |
|    │ PHASE 5: Check (setImmediate)                                                               │    |
|    │ PHASE 6: Close Callbacks (socket.on('close'))                                               │    |
|    └──────────────────────────────────────────────┬──────────────────────────────────────────────┘    |
|                                                   │                                                   |
|                                                   ▼                                                   |
|                         Active Handles == 0? ──► [ Process Terminates ]                               |
+-------------------------------------------------------------------------------------------------------+
```

---

## 🏛️ PART 1: The JavaScript & V8 Engine Core (Points 1 to 7)

### 1. JavaScript Engine (V8)
* **What it does:** An open-source C++ engine (used in Google Chrome and Node.js) that translates high-level JavaScript code into machine code (0s and 1s) executed directly by the CPU.
* **Architecture:** Uses **JIT (Just-In-Time) compilation** to deliver C++-like execution speeds rather than relying on pure interpretation.
* **Interview Trap:** JavaScript is not inherently slow; V8 compiles hot JavaScript code directly into native machine instructions at runtime.

### 2. Scanner & Parser (Eager vs Lazy Parsing)
* **What it does:** Breaks raw source text into tokens (lexical analysis) and verifies syntax rules before running any code.
* **Eager Parser (Full):** Parses code required immediately for startup into an Abstract Syntax Tree (AST).
* **Lazy Parser (Pre-parser):** Defers parsing of uncalled functions until they are actually invoked, saving memory and speeding up boot time.
* **Key Takeaway:** Syntax errors are caught during this parsing phase before execution begins.

### 3. Abstract Syntax Tree (AST)
* **What it is:** A hierarchical tree data structure representing the structural blueprint of your code (variables, statements, function calls).
* **Why it matters:** V8 cannot generate bytecode directly from string text; it relies on the AST. Tools like Babel, ESLint, and Prettier also work on the AST.

### 4. Ignition (The Bytecode Interpreter)
* **What it does:** Converts the AST into clean, register-based **Bytecode** and begins execution immediately.
* **Why Bytecode?** Compiling entire files to machine code at once requires too much RAM and causes slow startup. Bytecode allows instant startup with a minimal memory footprint.

### 5. TurboFan (Optimizing JIT Compiler & Hidden Classes)
* **What it does:** While Ignition executes bytecode, a **Profiler (Type Feedback Vector)** monitors hot functions that run repeatedly. TurboFan compiles this hot code into optimized native machine code.
* **Hidden Classes (Shapes):** JavaScript objects are dynamic, but V8 assigns hidden C++-like structural shapes behind the scenes for ultra-fast property lookups.
* **De-optimization (Bailout):** If variable types change unexpectedly (e.g., passing a string into a function that previously only processed integers), TurboFan discards the machine code and drops back to Ignition bytecode.

### 6. Memory Allocation (Call Stack vs Memory Heap)
* **Stack Memory:** Stores primitive values (`number`, `string`, `boolean`, `null`, `undefined`, `symbol`, `bigint`), execution context frames, and pointer addresses. It is fast and has a fixed size.
* **Memory Heap:** A large, unorganized memory pool where dynamic data like **Objects, Arrays, and Closures** are stored. The Call Stack holds the pointer referencing the Heap.
* **Key Trap:** `const obj = {}` allows mutating properties because the pointer on the Stack is locked, while the heap object remains mutable.

### 7. Orinoco (The Garbage Collector)
* **What it does:** Automatically frees unused heap memory using a generational memory model:
* **New Space (Young Generation):** Uses the fast **Scavenger (Cheney's Copying Algorithm)** to clear short-lived objects in milliseconds.
* **Old Space (Tenured Generation):** Objects that survive multiple garbage collection cycles are promoted here and cleaned using the **Mark-Sweep-Compact** algorithm.

---

## ⚙️ PART 2: Execution Context & Single-Thread Mechanics (Points 8 to 10)

### 8. Execution Context
* **What it is:** The runtime environment created whenever JavaScript code runs.
* **Phase 1 (Memory Creation / Hoisting):** Variables are allocated in memory. `var` is initialized with `undefined`, functions are stored in full, and `let`/`const` are allocated but kept uninitialized in the **Temporal Dead Zone (TDZ)**.
* **Phase 2 (Code Execution):** Code executes line by line from top to bottom, assigning real values to variables.

### 9. Call Stack (LIFO Execution)
* **What it does:** A **Last In, First Out (LIFO)** data structure tracking active execution frames.
* **How it works:** Function invocations push a frame onto the stack; function returns pop it off.
* **Stack Overflow:** Unbounded recursion without a base case exceeds the memory limit, throwing `RangeError: Maximum call stack size exceeded`.

### 10. Synchronous vs Asynchronous Principle
* **Synchronous:** JavaScript has only one Call Stack and one Main Thread. It executes one command at a time in sequence (blocking).
* **Asynchronous:** To prevent freezing the main thread on slow tasks (network requests, timers, disk I/O), JavaScript delegates the task to the runtime and immediately continues executing subsequent code.

---

## 🟢 PART 3: Complete Node.js Program Execution Journey (Points 11 to 16)

### 11. The `node app.js` C++ Bootstrap
When you execute `node app.js` in your terminal:
1. An OS process is launched (`node.exe`).
2. A single **V8 Isolate** (independent execution instance with its own Heap and Stack) is initialized.
3. A **Libuv Event Loop** instance is created.
4. A **Libuv Worker Thread Pool** (default: 4 background C++ threads) is spawned for blocking operations.
5. Node.js environment utilities (`process`, `Buffer`, native C++ bindings) are registered.

### 12. The Node.js Module Wrapper Function (IIFE)
Before execution, Node.js invisibly wraps the contents of your file in an IIFE:
```javascript
(function (exports, require, module, __filename, __dirname) {
  // YOUR APP.JS CODE LIVES HERE
});
```

### 13. Libuv Concurrency Architecture (Kernel vs Thread Pool)
* **Path A: OS Kernel Non-Blocking I/O (0 Threads Used):** Network sockets, TCP/HTTP connections, and incoming web requests are delegated directly to the OS kernel using event notification interfaces (**epoll** on Linux, **kqueue** on macOS, **IOCP** on Windows). Thousands of concurrent requests run without blocking threads.
* **Path B: Libuv Worker Thread Pool (4 Default Threads):** Operations that cannot be handled non-blockingly by OS kernels are delegated to Libuv's thread pool (`fs` file operations, `crypto.pbkdf2`, `dns.lookup`, `zlib`).

### 14. The Node.js Event Loop (6 Phases)
1. **Timers Phase:** Executes callbacks from expired `setTimeout()` and `setInterval()`.
2. **Pending Callbacks Phase:** Executes deferred I/O callbacks & system errors (TCP).
3. **Idle, Prepare Phase:** Internal Libuv coordination tasks only.
4. **Poll Phase (I/O):** Retrieves new I/O events from epoll/IOCP, executes I/O callbacks, and waits if no timers are scheduled.
5. **Check Phase:** Executes `setImmediate()` callbacks.
6. **Close Callbacks Phase:** Executes socket/handle close events (`socket.on('close')`).

### 15. Node.js Microtask Priorities: `process.nextTick` vs Promises
* **VIP Priority 1 — `process.nextTick` Queue:** Executes immediately after current operation completes, before any Promise microtasks.
* **VIP Priority 2 — Promise Microtask Queue:** Handles resolved Promise callbacks (`.then()`, `.catch()`) and `queueMicrotask()`.
* **The Rule:** The `process.nextTick` queue is drained completely first, followed by the Promise microtask queue, before the event loop advances to the next phase.

### 16. Event Loop Termination Rule (Active Handles & Requests)
* Node.js keeps count of all **Active Handles** (open network servers, open sockets, active timers) and **Active Requests** (ongoing file reads, DNS queries).
* As long as `active_handles > 0` or `active_requests > 0`, the process remains alive.
* The moment the counter reaches zero, the event loop exits and the Node.js process terminates cleanly.

---

## 🚀 PART 4: Concurrency & Scaling Solutions (Points 17 to 18)

### 17. Worker Threads (`worker_threads`)
* **Why it is needed:** JavaScript is single-threaded. CPU-bound operations (image resizing, video encoding, password hashing, large array processing) block the Call Stack and freeze the event loop.
* **What it does:** Creates **Multi-Threading within the same OS process**. Each worker thread has its own isolated V8 engine and event loop, but can share memory with the parent thread via `SharedArrayBuffer`.
* **Best used for:** CPU-heavy computations.

### 18. Cluster Module (`cluster`)
* **Why it is needed:** Node.js runs on a single CPU core by default. On a modern server with 8 or 16 cores, the remaining cores remain completely idle.
* **What it does:** Enables **Multi-Processing across multiple CPU cores**. It forks child processes (each with its own isolated memory and PID) that share the same server port (e.g., port 3000) using Round-Robin load balancing.
* **Best used for:** Scaling web traffic throughput and zero-downtime server reloads (commonly managed in production using PM2 Cluster Mode).

---

## 📚 PART 5: ALL 68 MISSING SLIDES MASTER CURRICULUM (Slides 125 to 192)

---

### 📂 Module 11: Scope, Hoisting & Closures (Slides 125 – 132)

#### Slide 125: Q. What is Execution Context & how does JS execute code? ⭐ V. IMP
* **Answer:** An Execution Context is an abstract environment created by V8 to execute JS code. It contains two components:
  1. *Memory Creation Phase:* Allocates variables and functions (`var` is set to `undefined`, functions are copied completely, `let`/`const` are uninitialized).
  2. *Code Execution Phase:* Executes code line-by-line single-threaded on the Call Stack, assigning values.

#### Slide 126: Q. What is Temporal Dead Zone (TDZ) & difference between var, let, const hoisting? ⭐ V. IMP
* **Answer:** All variables (`var`, `let`, `const`) are hoisted. The difference is:
  * `var` is initialized with `undefined`.
  * `let` and `const` remain `<uninitialized>` in memory from the start of the block until the declaration line. Accessing them during this window throws a `ReferenceError`. This window is the **Temporal Dead Zone**.

#### Slide 127: Q. What is a Closure in JS & how does Lexical Scope work? ⭐ V. IMP
* **Answer:** A closure is a function bundled together with its lexical environment. Even after an outer function has returned and been popped off the Call Stack, the inner function retains access to outer variables via its internal `[[Scopes]]` reference.

#### Slide 128: Q. How to use Closures for Data Privacy / Encapsulation? (Private Variables)
* **Answer:** Variables declared inside an outer function cannot be accessed or modified from the outside scope, creating true encapsulation:
```javascript
function createWallet(initialAmount) {
  let balance = initialAmount; // Private variable
  return {
    addFunds: (amount) => { balance += amount; },
    getBalance: () => balance
  };
}
const myWallet = createWallet(500);
myWallet.addFunds(200);
console.log(myWallet.getBalance()); // 700
console.log(myWallet.balance); // undefined (Protected!)
```

#### Slide 129: Q. Explain setTimeout in for-loop problem with var vs let & its Closure solution ⭐ V. IMP
* **Answer:**
  * `var` is function-scoped. A single shared `i` variable exists, which equals `3` when the timer expires.
  * `let` is block-scoped. Each loop iteration creates a fresh lexical scope and closure holding that iteration's value (`0, 1, 2`).
  * *IIFE Solution with var:* Pass `i` into an Immediately Invoked Function Expression to capture a local parameter copy.

#### Slide 130: Q. What are the 4 Binding Rules of "this" keyword in JavaScript? ⭐ V. IMP
* **Answer (in order of precedence):**
  1. `new` Binding: `new MyClass()` binds `this` to the newly allocated object.
  2. Explicit Binding: `.call()`, `.apply()`, `.bind()` explicitly define `this`.
  3. Implicit Binding: `obj.method()` binds `this` to the object before the dot (`obj`).
  4. Default Binding: Standalone function calls bind `this` to `window` (or `undefined` in strict mode).

#### Slide 131: Q. Difference between Regular Functions and Arrow Functions ("this" & arguments)
* **Answer:** Arrow functions do NOT have their own `this`, `arguments`, `super`, or `new.target`. They inherit `this` lexically from their enclosing parent scope. Their `this` cannot be altered by `call`, `apply`, or `bind`.

#### Slide 132: Q. What is Function Memoization & how to implement memoize() using Closures?
* **Answer:** Memoization caches function results based on arguments to prevent expensive recalculations:
```javascript
function memoize(fn) {
  const cache = {};
  return function(...args) {
    const key = JSON.stringify(args);
    if (key in cache) return cache[key];
    return (cache[key] = fn.apply(this, args));
  };
}
```

---

### 📂 Module 12: Asynchronous JS, Promises & Event Loop (Slides 133 – 144)

#### Slide 133: Q. What is the JavaScript Event Loop? (Call Stack, Web APIs & Queues) ⭐ V. IMP
* **Answer:** A coordinator that constantly checks if the Call Stack is empty. When empty, it transfers queued asynchronous callbacks (Microtasks first, then Macrotasks) onto the Call Stack for execution.

#### Slide 134: Q. What is the difference between Microtask Queue and Macrotask Queue? ⭐ V. IMP
* **Answer:**
  * *Microtask Queue:* High-priority queue for Promises (`.then`, `.catch`), `queueMicrotask`, and `MutationObserver`. It must be completely drained to 0 before anything else runs.
  * *Macrotask Queue:* Holds `setTimeout`, `setInterval`, and I/O callbacks. Only 1 task runs per tick.

#### Slide 135: Q. What is Callback Hell (Pyramid of Doom) & Inversion of Control?
* **Answer:**
  * *Callback Hell:* Deeply nested callbacks forming a pyramid shape, making error handling and readability difficult.
  * *Inversion of Control:* Giving control of your execution to a third-party callback, unsure if it will run zero times, once, or multiple times. Promises solve this by returning an immutable promise object.

#### Slide 136: Q. What are Promises in JS? Explain Promise States (Pending, Fulfilled, Rejected) ⭐ V. IMP
* **Answer:** An object representing the eventual completion or failure of an asynchronous operation. States:
  1. `Pending`: Initial state.
  2. `Fulfilled`: Completed successfully (`resolve(value)`).
  3. `Rejected`: Failed (`reject(error)`). Once settled, state cannot change.

#### Slide 137: Q. How does Promise Chaining & Error Handling (.catch, .finally) work?
* **Answer:** Every `.then()` returns a new Promise, allowing chained async steps. Any error thrown along the chain bypasses intermediate `.then` handlers until caught by `.catch()`. `.finally()` executes regardless of success or failure.

#### Slide 138: Q. What is the difference between Promise.all() and Promise.allSettled()? ⭐ V. IMP
* **Answer:**
  * `Promise.all([p1, p2])`: Fails fast. If any single promise rejects, the whole call rejects immediately.
  * `Promise.allSettled([p1, p2])`: Never rejects. Waits for all promises to finish and returns an array of objects with `{ status: 'fulfilled', value }` or `{ status: 'rejected', reason }`.

#### Slide 139: Q. What is the difference between Promise.race() and Promise.any()?
* **Answer:**
  * `Promise.race()`: Resolves or rejects as soon as the *first* promise settles (useful for request timeouts).
  * `Promise.any()`: Resolves as soon as the *first* promise *fulfills* (ignores rejections until all fail with `AggregateError`).

#### Slide 140: Q. What is async / await & how does it simplify asynchronous code? ⭐ V. IMP
* **Answer:** Syntactic sugar built on top of Promises and Generators. An `async` function always returns a Promise. The `await` keyword pauses execution within the function without blocking the main thread, resuming once the Promise resolves.

#### Slide 141: Q. How to run Async operations in Parallel vs Sequential with async/await?
* **Answer:**
  * *Sequential:* Calling `await p1; await p2;` takes `time(p1) + time(p2)`.
  * *Parallel:* Calling `await Promise.all([p1, p2])` takes `max(time(p1), time(p2))`.

#### Slide 142: Q. How does Error Handling work in async/await using try...catch?
* **Answer:** Wrap `await` expressions in a `try...catch` block. Any rejection from the awaited Promise throws an error directly into the `catch` block.

#### Slide 143: Q. What is Fetch API & how to check response status (res.ok)?
* **Answer:** `fetch()` does not reject on HTTP error statuses (like 404 or 500); it only rejects on network failures. You must manually verify `if (!res.ok) throw new Error(res.statusText);`.

#### Slide 144: Q. How to cancel a network request using AbortController?
* **Answer:** Create `const controller = new AbortController()`, pass `{ signal: controller.signal }` to `fetch()`, and invoke `controller.abort()` when the user navigates away or types new input.

---

### 📂 Module 13: Prototypes & OOP in JavaScript (Slides 145 – 152)

#### Slide 145: Q. What are Prototypes & how does Prototype Chain work in JS? ⭐ V. IMP
* **Answer:** Every object in JS has an internal link to another object called its prototype. When accessing a property, JS checks the object itself, then traverses up the prototype chain (`__proto__`) until it hits `Object.prototype`, and finally `null`.

#### Slide 146: Q. What is the difference between __proto__ and prototype property? ⭐ V. IMP
* **Answer:**
  * `prototype`: A property existing only on constructor functions and classes. It acts as the blueprint template for future instances.
  * `__proto__`: An accessor property on object instances pointing to their actual prototype in memory (`instance.__proto__ === Constructor.prototype`).

#### Slide 147: Q. What is Prototypal Inheritance & how does Object.create() work? ⭐ V. IMP
* **Answer:** Objects inheriting properties and methods directly from other objects without requiring a `class`. `Object.create(proto)` creates a new empty object whose `__proto__` is set explicitly to `proto`.

#### Slide 148: Q. What happens internally when you call a function with "new" keyword? ⭐ V. IMP
* **Answer:**
  1. A new empty object is created: `{}`.
  2. Its `__proto__` is linked to `Constructor.prototype`.
  3. The constructor is called with `this` bound to the new object.
  4. Returns the new object (unless the constructor explicitly returns a different object).

#### Slide 149: Q. What are ES6 Classes & how do constructor, extends, and super work?
* **Answer:** Classes are syntactic sugar over prototypal inheritance. `extends` sets up the prototype chain link between child and parent prototypes. `super()` calls the parent constructor with the current instance context.

#### Slide 150: Q. How to define Private fields (#field) and Static methods in ES6 Classes?
* **Answer:**
  * Prefixing a variable with `#` (e.g., `#balance = 0`) creates a hard private field inaccessible outside the class.
  * Prefixing a method with `static` binds it to the Class constructor itself, not instances.

#### Slide 151: Q. What is Prototype Pollution and how to protect objects from it?
* **Answer:** An attack where an attacker injects properties into `Object.prototype` (via payload keys like `__proto__`), polluting all objects globally. Protect against it using `Object.create(null)` or `Object.freeze(Object.prototype)`.

#### Slide 152: Q. Difference between Classical Inheritance vs Prototypal Inheritance?
* **Answer:**
  * *Classical (Java/C++):* Classes act as blueprints; objects are instantiated as separate static copies.
  * *Prototypal (JS):* Objects link directly to other objects in memory via dynamic prototype delegation.

---

### 📂 Module 14: Advanced Array & Object Methods (Slides 153 – 160)

#### Slide 153: Q. What is reduce() method in Array & how to group/transform data? ⭐ V. IMP
* **Answer:** Iterates over an array and reduces it to a single value (number, object, or array) using an accumulator:
```javascript
const items = [{ cat: "Fruit", name: "Apple" }, { cat: "Fruit", name: "Banana" }, { cat: "Dairy", name: "Milk" }];
const grouped = items.reduce((acc, item) => {
  acc[item.cat] = acc[item.cat] || [];
  acc[item.cat].push(item.name);
  return acc;
}, {});
```

#### Slide 154: Q. What is the difference between some() and every() methods in Array?
* **Answer:**
  * `some()`: Returns `true` if at least *one* element satisfies the predicate (short-circuits on first true).
  * `every()`: Returns `true` only if *all* elements satisfy the predicate (short-circuits on first false).

#### Slide 155: Q. What are flat() and flatMap() methods in Array?
* **Answer:**
  * `flat(depth)`: Flattens sub-array elements recursively up to the specified depth (`[1, [2, [3]]].flat(2)` $\rightarrow$ `[1, 2, 3]`).
  * `flatMap()`: Maps each element using a mapping function and flattens the result by 1 level.

#### Slide 156: Q. What is the difference between Object.freeze() and Object.seal()? ⭐ V. IMP
* **Answer:**
  * `Object.freeze()`: Prevents adding, deleting, or modifying existing property values (read-only).
  * `Object.seal()`: Prevents adding or deleting properties, but allows modifying *existing* values. Both are shallow.

#### Slide 157: Q. What is Object.defineProperty() & Property Descriptors (writable, enumerable, configurable)?
* **Answer:** Allows setting granular property behaviors:
  * `writable`: If `false`, value cannot be changed.
  * `enumerable`: If `false`, hidden from `for...in` and `Object.keys()`.
  * `configurable`: If `false`, property cannot be deleted or re-configured.

#### Slide 158: Q. What is structuredClone() for Deep Copy & why is it better than JSON.parse()? ⭐ V. IMP
* **Answer:** `structuredClone()` is the modern native JS deep-cloning API. Unlike `JSON.parse(JSON.stringify())`, it supports circular references, `Date`, `RegExp`, `Map`, `Set`, and `TypedArrays` without breaking data types.

#### Slide 159: Q. What are ES2023 Non-mutating Array methods: toSorted(), toReversed(), toSpliced()?
* **Answer:** Modern array methods that return a modified copy of the array without mutating the original source array (`toSorted()`, `toReversed()`, `toSpliced()`, `with()`).

#### Slide 160: Q. What are Object.keys(), Object.values(), and Object.entries()?
* **Answer:**
  * `Object.keys(obj)`: Returns an array of enumerable property names.
  * `Object.values(obj)`: Returns an array of enumerable property values.
  * `Object.entries(obj)`: Returns an array of `[key, value]` pairs.

---

### 📂 Module 15: Modern ES6+ & Metaprogramming (Slides 161 – 168)

#### Slide 161: Q. What is the difference between Nullish Coalescing (??) and Logical OR (||)? ⭐ V. IMP
* **Answer:**
  * `||` returns the fallback for any falsy value (`false`, `0`, `""`, `null`, `undefined`, `NaN`).
  * `??` returns the fallback only for `null` and `undefined`, preserving valid falsy values like `0` or `""`.

#### Slide 162: Q. What is Optional Chaining (?.) & how does it prevent runtime errors? ⭐ V. IMP
* **Answer:** Safely accesses nested object properties (`user?.address?.city`). If any reference is `null` or `undefined`, evaluation short-circuits and returns `undefined` instead of throwing a `TypeError`.

#### Slide 163: Q. What is the Symbol primitive & why is it used for unique object properties?
* **Answer:** A unique and immutable primitive data type. Used to create non-colliding object keys and implement well-known language protocols like `Symbol.iterator`.

#### Slide 164: Q. What is BigInt & why is it needed in JavaScript?
* **Answer:** JavaScript's standard `Number` type is safe only up to $2^{53} - 1$ (`Number.MAX_SAFE_INTEGER`). `BigInt` allows arbitrary precision integers for large calculations (e.g., `9007199254740991n + 2n`).

#### Slide 165: Q. What are WeakMap and WeakSet & how do they prevent Memory Leaks? ⭐ V. IMP
* **Answer:** Collections where object keys/values are held as "weak references". If an object has no other references in memory, the Garbage Collector reclaims it automatically, preventing memory leaks when storing DOM metadata.

#### Slide 166: Q. What are Generators and Iterators (function*, yield, next)?
* **Answer:** A generator function (`function*`) can pause its execution using `yield` and resume when its iterator's `.next()` method is called. Useful for handling data streams and custom lazy iterables.

#### Slide 167: Q. What is Proxy and Reflect API & how does modern framework Reactivity work? ⭐ V. IMP
* **Answer:** A `Proxy` wraps an object and intercepts basic operations (get, set, delete) using traps. Frameworks like Vue 3 use Proxy to track when state is read (dependency tracking) or updated (triggering UI re-renders).

#### Slide 168: Q. Difference between ES Modules (import/export) and CommonJS (require/exports)?
* **Answer:**
  * *CommonJS (CJS):* Synchronous, dynamic loading at runtime via `require()`. Used traditionally in Node.js.
  * *ES Modules (ESM):* Asynchronous, static analysis at compile time via `import`/`export`, allowing dead-code elimination (tree-shaking).

---

### 📂 Module 16: Browser Internals & Web Performance (Slides 169 – 176)

#### Slide 169: Q. What is Critical Rendering Path (CRP)? How does browser render HTML/CSS? ⭐ V. IMP
* **Answer:** The sequence of steps the browser takes to convert code into pixels:
  1. Construct DOM Tree from HTML.
  2. Construct CSSOM Tree from CSS.
  3. Combine into Render Tree.
  4. Layout (Reflow): Calculate exact element geometry.
  5. Paint (Repaint): Fill pixels on screen.
  6. Composite: Merge GPU layers.

#### Slide 170: Q. What is the difference between Reflow (Layout) and Repaint? How to minimize Reflow? ⭐ V. IMP
* **Answer:**
  * *Reflow:* Calculating geometry/dimensions (expensive). Triggered by width, height, font-size changes.
  * *Repaint:* Redrawing pixels without altering geometry (color, background).
  * *Optimization:* Batch DOM changes with `DocumentFragment` and use CSS GPU transforms (`transform`, `opacity`).

#### Slide 171: Q. What is the difference between <script>, <script async>, and <script defer>? ⭐ V. IMP
* **Answer:**
  * `<script>`: Pauses HTML parsing while downloading and executing.
  * `<script async>`: Downloads asynchronously, but pauses HTML parsing immediately upon download to execute (unordered execution).
  * `<script defer>`: Downloads asynchronously and executes only after HTML parsing completes in order.

#### Slide 172: Q. What is IntersectionObserver API & how to implement Image Lazy Loading? ⭐ V. IMP
* **Answer:** An API that asynchronously observes when target elements enter or exit the viewport, replacing expensive `window.onscroll` handlers for lazy loading images and infinite scrolling.

#### Slide 173: Q. Difference between Cookies, localStorage, sessionStorage, and IndexedDB? ⭐ V. IMP
* **Answer:**
  * *Cookies (~4KB):* Sent automatically with HTTP requests; supports `HttpOnly` and `SameSite` flags.
  * *localStorage (~5-10MB):* Persistent client-side key-value storage.
  * *sessionStorage (~5MB):* Scoped to the browser tab lifetime.
  * *IndexedDB (>250MB):* Transactional NoSQL database for large structured offline data.

#### Slide 174: Q. What is Garbage Collection in V8 & how does Mark-and-Sweep work?
* **Answer:** The engine roots (Global object, call stack) traverse all references. Objects that cannot be reached are marked as unreachable and swept (deleted) from memory.

#### Slide 175: Q. What are common Memory Leaks in JS & how to debug them using Chrome DevTools? ⭐ V. IMP
* **Answer:**
  * *Causes:* Accidental globals, uncleared `setInterval`, closures retaining unused variables, detached DOM nodes.
  * *Debugging:* Open Chrome DevTools $\rightarrow$ Memory tab $\rightarrow$ Take Heap Snapshot $\rightarrow$ Filter by "Detached" or compare two snapshots to locate retaining paths.

#### Slide 176: Q. What are Core Web Vitals (LCP, INP, CLS) and how to optimize them in JS?
* **Answer:**
  * *LCP (Largest Contentful Paint):* Measures loading speed. Optimize with image compression and SSR.
  * *INP (Interaction to Next Paint):* Measures responsiveness. Optimize by keeping event handlers non-blocking.
  * *CLS (Cumulative Layout Shift):* Measures visual stability. Optimize by setting explicit width/height on images.

---

### 📂 Module 17: Web Security & Hardening (Slides 177 – 182)

#### Slide 177: Q. What is CORS & how does Preflight OPTIONS request work? ⭐ V. IMP
* **Answer:** A browser security mechanism preventing cross-origin requests unless authorized by the server. If a request includes non-standard headers (`Authorization`, `application/json`), the browser sends an automatic preflight `OPTIONS` check first.

#### Slide 178: Q. What is Cross-Site Scripting (XSS) & why is innerHTML dangerous? ⭐ V. IMP
* **Answer:** An attack where malicious JavaScript is injected into user sessions. `innerHTML` executes unescaped `<script>` or `<img onerror>` payloads. Prevent by using `textContent`, sanitizing with DOMPurify, and using CSP headers.

#### Slide 179: Q. What is Cross-Site Request Forgery (CSRF) & how do SameSite cookies prevent it? ⭐ V. IMP
* **Answer:** Tricks an authenticated user's browser into executing unwanted actions on a trusted site. Prevent by using `SameSite=Strict` or `SameSite=Lax` on cookies and validating Anti-CSRF tokens.

#### Slide 180: Q. What is Content Security Policy (CSP)?
* **Answer:** An HTTP response header (`Content-Security-Policy`) that specifies trusted domains for scripts, styles, and images, mitigating XSS and data injection attacks.

#### Slide 181: Q. What is "use strict" mode & what differences does it make?
* **Answer:** Enforces stricter parsing: prevents accidental global variable creation, throws errors on silent failures, eliminates duplicate parameter names, and sets `this === undefined` in plain functions.

#### Slide 182: Q. What is Same-Origin Policy (SOP)?
* **Answer:** A core browser security model preventing a script loaded from one origin (`protocol + domain + port`) from accessing DOM or data from another origin.

---

### 📂 Module 18: Machine Coding Polyfills (Slides 183 – 192)

#### Slide 183: Q. How to implement custom Array.prototype.myMap() polyfill? ⭐ V. IMP
```javascript
Array.prototype.myMap = function(callback) {
  if (typeof callback !== "function") throw new TypeError("Callback must be a function");
  const result = [];
  for (let i = 0; i < this.length; i++) {
    if (i in this) result.push(callback(this[i], i, this));
  }
  return result;
};
```

#### Slide 184: Q. How to implement custom Array.prototype.myFilter() polyfill? ⭐ V. IMP
```javascript
Array.prototype.myFilter = function(callback) {
  const result = [];
  for (let i = 0; i < this.length; i++) {
    if (i in this && callback(this[i], i, this)) result.push(this[i]);
  }
  return result;
};
```

#### Slide 185: Q. How to implement custom Array.prototype.myReduce() polyfill? ⭐ V. IMP
```javascript
Array.prototype.myReduce = function(callback, initialValue) {
  let acc = initialValue;
  let startIdx = 0;
  if (acc === undefined) {
    if (this.length === 0) throw new TypeError("Reduce of empty array with no initial value");
    acc = this[0];
    startIdx = 1;
  }
  for (let i = startIdx; i < this.length; i++) {
    if (i in this) acc = callback(acc, this[i], i, this);
  }
  return acc;
};
```

#### Slide 186: Q. How to implement custom Function.prototype.myBind() polyfill? ⭐ V. IMP
```javascript
Function.prototype.myBind = function(context, ...args) {
  const fn = this;
  return function(...innerArgs) {
    return fn.apply(context, [...args, ...innerArgs]);
  };
};
```

#### Slide 187: Q. How to implement custom Array.prototype.myFlat() polyfill (Recursive)? ⭐ V. IMP
```javascript
Array.prototype.myFlat = function(depth = 1) {
  const result = [];
  (function flatten(arr, d) {
    for (const item of arr) {
      if (Array.isArray(item) && d < depth) {
        flatten(item, d + 1);
      } else {
        result.push(item);
      }
    }
  })(this, 0);
  return result;
};
```

#### Slide 188: Q. How to implement custom Promise.all() polyfill? ⭐ V. IMP
```javascript
Promise.myAll = function(promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let completed = 0;
    if (promises.length === 0) return resolve(results);
    promises.forEach((p, idx) => {
      Promise.resolve(p)
        .then(val => {
          results[idx] = val;
          completed++;
          if (completed === promises.length) resolve(results);
        })
        .catch(reject);
    });
  });
};
```

#### Slide 189: Q. How to implement custom debounce(fn, delay) function from scratch? ⭐ V. IMP
```javascript
function debounce(fn, delay) {
  let timerId;
  return function(...args) {
    clearTimeout(timerId);
    timerId = setTimeout(() => fn.apply(this, args), delay);
  };
}
```

#### Slide 190: Q. How to implement custom throttle(fn, limit) function from scratch? ⭐ V. IMP
```javascript
function throttle(fn, limit) {
  let inThrottle = false;
  return function(...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
```

#### Slide 191: Q. How to implement custom Event Emitter / Pub-Sub pattern (on, emit, off)? ⭐ V. IMP
```javascript
class EventEmitter {
  constructor() { this.events = {}; }
  on(event, listener) {
    (this.events[event] = this.events[event] || []).push(listener);
  }
  emit(event, ...args) {
    (this.events[event] || []).forEach(fn => fn(...args));
  }
  off(event, listener) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(fn => fn !== listener);
  }
}
```

#### Slide 192: Q. How to implement custom deepClone(obj) handling circular references? ⭐ V. IMP
```javascript
function deepClone(obj, hash = new WeakMap()) {
  if (obj === null || typeof obj !== "object") return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof RegExp) return new RegExp(obj);
  if (hash.has(obj)) return hash.get(obj); // Cycle detection

  const clone = Array.isArray(obj) ? [] : {};
  hash.set(obj, clone);
  for (const key of Reflect.ownKeys(obj)) {
    clone[key] = deepClone(obj[key], hash);
  }
  return clone;
}
```

---

## ⏱️ Node.js Complete Execution Order Example

```javascript
const fs = require("fs");

console.log("1: Synchronous Start");

setTimeout(() => {
  console.log("2: setTimeout Timer");
}, 0);

setImmediate(() => {
  console.log("3: setImmediate Check");
});

Promise.resolve().then(() => {
  console.log("4: Promise Microtask");
});

process.nextTick(() => {
  console.log("5: process.nextTick Super VIP");
});

console.log("6: Synchronous End");
```

### Execution Flow:
1. `1: Synchronous Start` prints immediately on the Call Stack.
2. `setTimeout` registers with Libuv Timers phase.
3. `setImmediate` registers with Libuv Check phase.
4. `Promise.then` enters the Promise Microtask Queue.
5. `process.nextTick` enters the `nextTick` Queue.
6. `6: Synchronous End` prints on the Call Stack.
7. **Call Stack is now empty:**
   * **`process.nextTick`** runs first $\rightarrow$ Prints `5`.
   * **Promise Microtask** runs second $\rightarrow$ Prints `4`.
8. **Event Loop begins its 6 phases:**
   * Timers Phase: `setTimeout` executes $\rightarrow$ Prints `2`.
   * Check Phase: `setImmediate` executes $\rightarrow$ Prints `3`.

**Final Output:**
```
1: Synchronous Start
6: Synchronous End
5: process.nextTick Super VIP
4: Promise Microtask
2: setTimeout Timer
3: setImmediate Check
```

---

## 🎙️ 90-Second Senior Fullstack Engineer Interview Speech (English)

> *"When a program runs in Node.js, the OS spawns a single process that initializes a **V8 Isolate** alongside a **Libuv Event Loop** and a background **Thread Pool** of 4 worker threads. Before execution, Node.js wraps the file in a **Module Wrapper IIFE** providing local file scoping and injecting `require`, `module`, and `exports`.*
>
> *The code is parsed into an **AST**, converted to bytecode by **Ignition**, and optimized to machine code by **TurboFan** using **Hidden Classes**. Synchronous operations run on the single-threaded **Call Stack**, with memory managed between the **Stack** and **Heap** and reclaimed by the **Orinoco Garbage Collector**.*
>
> *Asynchronous network I/O is offloaded to the **OS Kernel** without blocking threads using interfaces like epoll or IOCP, while file and crypto operations use the **Libuv Thread Pool**. When tasks complete, callbacks enter queues coordinated by the **Event Loop's 6 Phases** (Timers, Pending, Idle, Poll, Check, Close).*
>
> *Between each phase, **`process.nextTick`** executes with highest VIP priority, followed by **Promise microtasks**. The process exits when active handles reach zero. Finally, to prevent CPU bottlenecks on the main thread, we use **Worker Threads**, and to scale across multi-core servers for high web traffic, we deploy the **Cluster Module** or PM2."*
