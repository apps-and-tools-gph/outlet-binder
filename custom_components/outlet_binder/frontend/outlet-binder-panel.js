//#region node_modules/@lit/reactive-element/css-tag.js
var e = globalThis, t = e.ShadowRoot && (e.ShadyCSS === void 0 || e.ShadyCSS.nativeShadow) && "adoptedStyleSheets" in Document.prototype && "replace" in CSSStyleSheet.prototype, n = Symbol(), r = /* @__PURE__ */ new WeakMap(), i = class {
	constructor(e, t, r) {
		if (this._$cssResult$ = !0, r !== n) throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");
		this.cssText = e, this.t = t;
	}
	get styleSheet() {
		let e = this.o, n = this.t;
		if (t && e === void 0) {
			let t = n !== void 0 && n.length === 1;
			t && (e = r.get(n)), e === void 0 && ((this.o = e = new CSSStyleSheet()).replaceSync(this.cssText), t && r.set(n, e));
		}
		return e;
	}
	toString() {
		return this.cssText;
	}
}, a = (e) => new i(typeof e == "string" ? e : e + "", void 0, n), o = (e, ...t) => new i(e.length === 1 ? e[0] : t.reduce((t, n, r) => t + ((e) => {
	if (!0 === e._$cssResult$) return e.cssText;
	if (typeof e == "number") return e;
	throw Error("Value passed to 'css' function must be a 'css' function result: " + e + ". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");
})(n) + e[r + 1], e[0]), e, n), s = (n, r) => {
	if (t) n.adoptedStyleSheets = r.map((e) => e instanceof CSSStyleSheet ? e : e.styleSheet);
	else for (let t of r) {
		let r = document.createElement("style"), i = e.litNonce;
		i !== void 0 && r.setAttribute("nonce", i), r.textContent = t.cssText, n.appendChild(r);
	}
}, c = t ? (e) => e : (e) => e instanceof CSSStyleSheet ? ((e) => {
	let t = "";
	for (let n of e.cssRules) t += n.cssText;
	return a(t);
})(e) : e, { is: l, defineProperty: u, getOwnPropertyDescriptor: d, getOwnPropertyNames: f, getOwnPropertySymbols: ee, getPrototypeOf: te } = Object, p = globalThis, ne = p.trustedTypes, re = ne ? ne.emptyScript : "", ie = p.reactiveElementPolyfillSupport, ae = (e, t) => e, oe = {
	toAttribute(e, t) {
		switch (t) {
			case Boolean:
				e = e ? re : null;
				break;
			case Object:
			case Array: e = e == null ? e : JSON.stringify(e);
		}
		return e;
	},
	fromAttribute(e, t) {
		let n = e;
		switch (t) {
			case Boolean:
				n = e !== null;
				break;
			case Number:
				n = e === null ? null : Number(e);
				break;
			case Object:
			case Array: try {
				n = JSON.parse(e);
			} catch {
				n = null;
			}
		}
		return n;
	}
}, se = (e, t) => !l(e, t), ce = {
	attribute: !0,
	type: String,
	converter: oe,
	reflect: !1,
	useDefault: !1,
	hasChanged: se
};
Symbol.metadata ??= Symbol("metadata"), p.litPropertyMetadata ??= /* @__PURE__ */ new WeakMap();
var m = class extends HTMLElement {
	static addInitializer(e) {
		this._$Ei(), (this.l ??= []).push(e);
	}
	static get observedAttributes() {
		return this.finalize(), this._$Eh && [...this._$Eh.keys()];
	}
	static createProperty(e, t = ce) {
		if (t.state && (t.attribute = !1), this._$Ei(), this.prototype.hasOwnProperty(e) && ((t = Object.create(t)).wrapped = !0), this.elementProperties.set(e, t), !t.noAccessor) {
			let n = Symbol(), r = this.getPropertyDescriptor(e, n, t);
			r !== void 0 && u(this.prototype, e, r);
		}
	}
	static getPropertyDescriptor(e, t, n) {
		let { get: r, set: i } = d(this.prototype, e) ?? {
			get() {
				return this[t];
			},
			set(e) {
				this[t] = e;
			}
		};
		return {
			get: r,
			set(t) {
				let a = r?.call(this);
				i?.call(this, t), this.requestUpdate(e, a, n);
			},
			configurable: !0,
			enumerable: !0
		};
	}
	static getPropertyOptions(e) {
		return this.elementProperties.get(e) ?? ce;
	}
	static _$Ei() {
		if (this.hasOwnProperty(ae("elementProperties"))) return;
		let e = te(this);
		e.finalize(), e.l !== void 0 && (this.l = [...e.l]), this.elementProperties = new Map(e.elementProperties);
	}
	static finalize() {
		if (this.hasOwnProperty(ae("finalized"))) return;
		if (this.finalized = !0, this._$Ei(), this.hasOwnProperty(ae("properties"))) {
			let e = this.properties, t = [...f(e), ...ee(e)];
			for (let n of t) this.createProperty(n, e[n]);
		}
		let e = this[Symbol.metadata];
		if (e !== null) {
			let t = litPropertyMetadata.get(e);
			if (t !== void 0) for (let [e, n] of t) this.elementProperties.set(e, n);
		}
		this._$Eh = /* @__PURE__ */ new Map();
		for (let [e, t] of this.elementProperties) {
			let n = this._$Eu(e, t);
			n !== void 0 && this._$Eh.set(n, e);
		}
		this.elementStyles = this.finalizeStyles(this.styles);
	}
	static finalizeStyles(e) {
		let t = [];
		if (Array.isArray(e)) {
			let n = new Set(e.flat(1 / 0).reverse());
			for (let e of n) t.unshift(c(e));
		} else e !== void 0 && t.push(c(e));
		return t;
	}
	static _$Eu(e, t) {
		let n = t.attribute;
		return !1 === n ? void 0 : typeof n == "string" ? n : typeof e == "string" ? e.toLowerCase() : void 0;
	}
	constructor() {
		super(), this._$Ep = void 0, this.isUpdatePending = !1, this.hasUpdated = !1, this._$Em = null, this._$Ev();
	}
	_$Ev() {
		this._$ES = new Promise((e) => this.enableUpdating = e), this._$AL = /* @__PURE__ */ new Map(), this._$E_(), this.requestUpdate(), this.constructor.l?.forEach((e) => e(this));
	}
	addController(e) {
		(this._$EO ??= /* @__PURE__ */ new Set()).add(e), this.renderRoot !== void 0 && this.isConnected && e.hostConnected?.();
	}
	removeController(e) {
		this._$EO?.delete(e);
	}
	_$E_() {
		let e = /* @__PURE__ */ new Map(), t = this.constructor.elementProperties;
		for (let n of t.keys()) this.hasOwnProperty(n) && (e.set(n, this[n]), delete this[n]);
		e.size > 0 && (this._$Ep = e);
	}
	createRenderRoot() {
		let e = this.shadowRoot ?? this.attachShadow(this.constructor.shadowRootOptions);
		return s(e, this.constructor.elementStyles), e;
	}
	connectedCallback() {
		this.renderRoot ??= this.createRenderRoot(), this.enableUpdating(!0), this._$EO?.forEach((e) => e.hostConnected?.());
	}
	enableUpdating(e) {}
	disconnectedCallback() {
		this._$EO?.forEach((e) => e.hostDisconnected?.());
	}
	attributeChangedCallback(e, t, n) {
		this._$AK(e, n);
	}
	_$ET(e, t) {
		let n = this.constructor.elementProperties.get(e), r = this.constructor._$Eu(e, n);
		if (r !== void 0 && !0 === n.reflect) {
			let i = (n.converter?.toAttribute === void 0 ? oe : n.converter).toAttribute(t, n.type);
			this._$Em = e, i == null ? this.removeAttribute(r) : this.setAttribute(r, i), this._$Em = null;
		}
	}
	_$AK(e, t) {
		let n = this.constructor, r = n._$Eh.get(e);
		if (r !== void 0 && this._$Em !== r) {
			let e = n.getPropertyOptions(r), i = typeof e.converter == "function" ? { fromAttribute: e.converter } : e.converter?.fromAttribute === void 0 ? oe : e.converter;
			this._$Em = r;
			let a = i.fromAttribute(t, e.type);
			this[r] = a ?? this._$Ej?.get(r) ?? a, this._$Em = null;
		}
	}
	requestUpdate(e, t, n, r = !1, i) {
		if (e !== void 0) {
			let a = this.constructor;
			if (!1 === r && (i = this[e]), n ??= a.getPropertyOptions(e), !((n.hasChanged ?? se)(i, t) || n.useDefault && n.reflect && i === this._$Ej?.get(e) && !this.hasAttribute(a._$Eu(e, n)))) return;
			this.C(e, t, n);
		}
		!1 === this.isUpdatePending && (this._$ES = this._$EP());
	}
	C(e, t, { useDefault: n, reflect: r, wrapped: i }, a) {
		n && !(this._$Ej ??= /* @__PURE__ */ new Map()).has(e) && (this._$Ej.set(e, a ?? t ?? this[e]), !0 !== i || a !== void 0) || (this._$AL.has(e) || (this.hasUpdated || n || (t = void 0), this._$AL.set(e, t)), !0 === r && this._$Em !== e && (this._$Eq ??= /* @__PURE__ */ new Set()).add(e));
	}
	async _$EP() {
		this.isUpdatePending = !0;
		try {
			await this._$ES;
		} catch (e) {
			Promise.reject(e);
		}
		let e = this.scheduleUpdate();
		return e != null && await e, !this.isUpdatePending;
	}
	scheduleUpdate() {
		return this.performUpdate();
	}
	performUpdate() {
		if (!this.isUpdatePending) return;
		if (!this.hasUpdated) {
			if (this.renderRoot ??= this.createRenderRoot(), this._$Ep) {
				for (let [e, t] of this._$Ep) this[e] = t;
				this._$Ep = void 0;
			}
			let e = this.constructor.elementProperties;
			if (e.size > 0) for (let [t, n] of e) {
				let { wrapped: e } = n, r = this[t];
				!0 !== e || this._$AL.has(t) || r === void 0 || this.C(t, void 0, n, r);
			}
		}
		let e = !1, t = this._$AL;
		try {
			e = this.shouldUpdate(t), e ? (this.willUpdate(t), this._$EO?.forEach((e) => e.hostUpdate?.()), this.update(t)) : this._$EM();
		} catch (t) {
			throw e = !1, this._$EM(), t;
		}
		e && this._$AE(t);
	}
	willUpdate(e) {}
	_$AE(e) {
		this._$EO?.forEach((e) => e.hostUpdated?.()), this.hasUpdated || (this.hasUpdated = !0, this.firstUpdated(e)), this.updated(e);
	}
	_$EM() {
		this._$AL = /* @__PURE__ */ new Map(), this.isUpdatePending = !1;
	}
	get updateComplete() {
		return this.getUpdateComplete();
	}
	getUpdateComplete() {
		return this._$ES;
	}
	shouldUpdate(e) {
		return !0;
	}
	update(e) {
		this._$Eq &&= this._$Eq.forEach((e) => this._$ET(e, this[e])), this._$EM();
	}
	updated(e) {}
	firstUpdated(e) {}
};
m.elementStyles = [], m.shadowRootOptions = { mode: "open" }, m[ae("elementProperties")] = /* @__PURE__ */ new Map(), m[ae("finalized")] = /* @__PURE__ */ new Map(), ie?.({ ReactiveElement: m }), (p.reactiveElementVersions ??= []).push("2.1.2");
//#endregion
//#region node_modules/lit-html/lit-html.js
var le = globalThis, ue = (e) => e, de = le.trustedTypes, fe = de ? de.createPolicy("lit-html", { createHTML: (e) => e }) : void 0, pe = "$lit$", h = `lit$${Math.random().toFixed(9).slice(2)}$`, me = "?" + h, he = `<${me}>`, g = document, ge = () => g.createComment(""), _e = (e) => e === null || typeof e != "object" && typeof e != "function", ve = Array.isArray, ye = (e) => ve(e) || typeof e?.[Symbol.iterator] == "function", be = "[ 	\n\f\r]", xe = /<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g, Se = /-->/g, Ce = />/g, _ = RegExp(`>|${be}(?:([^\\s"'>=/]+)(${be}*=${be}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`, "g"), we = /'/g, Te = /"/g, Ee = /^(?:script|style|textarea|title)$/i, v = ((e) => (t, ...n) => ({
	_$litType$: e,
	strings: t,
	values: n
}))(1), y = Symbol.for("lit-noChange"), b = Symbol.for("lit-nothing"), De = /* @__PURE__ */ new WeakMap(), x = g.createTreeWalker(g, 129);
function Oe(e, t) {
	if (!ve(e) || !e.hasOwnProperty("raw")) throw Error("invalid template strings array");
	return fe === void 0 ? t : fe.createHTML(t);
}
var ke = (e, t) => {
	let n = e.length - 1, r = [], i, a = t === 2 ? "<svg>" : t === 3 ? "<math>" : "", o = xe;
	for (let t = 0; t < n; t++) {
		let n = e[t], s, c, l = -1, u = 0;
		for (; u < n.length && (o.lastIndex = u, c = o.exec(n), c !== null);) u = o.lastIndex, o === xe ? c[1] === "!--" ? o = Se : c[1] === void 0 ? c[2] === void 0 ? c[3] !== void 0 && (o = _) : (Ee.test(c[2]) && (i = RegExp("</" + c[2], "g")), o = _) : o = Ce : o === _ ? c[0] === ">" ? (o = i ?? xe, l = -1) : c[1] === void 0 ? l = -2 : (l = o.lastIndex - c[2].length, s = c[1], o = c[3] === void 0 ? _ : c[3] === "\"" ? Te : we) : o === Te || o === we ? o = _ : o === Se || o === Ce ? o = xe : (o = _, i = void 0);
		let d = o === _ && e[t + 1].startsWith("/>") ? " " : "";
		a += o === xe ? n + he : l >= 0 ? (r.push(s), n.slice(0, l) + pe + n.slice(l) + h + d) : n + h + (l === -2 ? t : d);
	}
	return [Oe(e, a + (e[n] || "<?>") + (t === 2 ? "</svg>" : t === 3 ? "</math>" : "")), r];
}, Ae = class e {
	constructor({ strings: t, _$litType$: n }, r) {
		let i;
		this.parts = [];
		let a = 0, o = 0, s = t.length - 1, c = this.parts, [l, u] = ke(t, n);
		if (this.el = e.createElement(l, r), x.currentNode = this.el.content, n === 2 || n === 3) {
			let e = this.el.content.firstChild;
			e.replaceWith(...e.childNodes);
		}
		for (; (i = x.nextNode()) !== null && c.length < s;) {
			if (i.nodeType === 1) {
				if (i.hasAttributes()) for (let e of i.getAttributeNames()) if (e.endsWith(pe)) {
					let t = u[o++], n = i.getAttribute(e).split(h), r = /([.?@])?(.*)/.exec(t);
					c.push({
						type: 1,
						index: a,
						name: r[2],
						strings: n,
						ctor: r[1] === "." ? Fe : r[1] === "?" ? Ie : r[1] === "@" ? Le : Pe
					}), i.removeAttribute(e);
				} else e.startsWith(h) && (c.push({
					type: 6,
					index: a
				}), i.removeAttribute(e));
				if (Ee.test(i.tagName)) {
					let e = i.textContent.split(h), t = e.length - 1;
					if (t > 0) {
						i.textContent = de ? de.emptyScript : "";
						for (let n = 0; n < t; n++) i.append(e[n], ge()), x.nextNode(), c.push({
							type: 2,
							index: ++a
						});
						i.append(e[t], ge());
					}
				}
			} else if (i.nodeType === 8) {
				if (i.data === me) c.push({
					type: 2,
					index: a
				});
				else {
					let e = -1;
					for (; (e = i.data.indexOf(h, e + 1)) !== -1;) c.push({
						type: 7,
						index: a
					}), e += h.length - 1;
				}
			}
			a++;
		}
	}
	static createElement(e, t) {
		let n = g.createElement("template");
		return n.innerHTML = e, n;
	}
};
function je(e, t, n = e, r) {
	if (t === y) return t;
	let i = r === void 0 ? n._$Cl : n._$Co?.[r], a = _e(t) ? void 0 : t._$litDirective$;
	return i?.constructor !== a && (i?._$AO?.(!1), a === void 0 ? i = void 0 : (i = new a(e), i._$AT(e, n, r)), r === void 0 ? n._$Cl = i : (n._$Co ??= [])[r] = i), i !== void 0 && (t = je(e, i._$AS(e, t.values), i, r)), t;
}
var Me = class {
	constructor(e, t) {
		this._$AV = [], this._$AN = void 0, this._$AD = e, this._$AM = t;
	}
	get parentNode() {
		return this._$AM.parentNode;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	u(e) {
		let { el: { content: t }, parts: n } = this._$AD, r = (e?.creationScope ?? g).importNode(t, !0);
		x.currentNode = r;
		let i = x.nextNode(), a = 0, o = 0, s = n[0];
		for (; s !== void 0;) {
			if (a === s.index) {
				let t;
				s.type === 2 ? t = new Ne(i, i.nextSibling, this, e) : s.type === 1 ? t = new s.ctor(i, s.name, s.strings, this, e) : s.type === 6 && (t = new Re(i, this, e)), this._$AV.push(t), s = n[++o];
			}
			a !== s?.index && (i = x.nextNode(), a++);
		}
		return x.currentNode = g, r;
	}
	p(e) {
		let t = 0;
		for (let n of this._$AV) n !== void 0 && (n.strings === void 0 ? n._$AI(e[t]) : (n._$AI(e, n, t), t += n.strings.length - 2)), t++;
	}
}, Ne = class e {
	get _$AU() {
		return this._$AM?._$AU ?? this._$Cv;
	}
	constructor(e, t, n, r) {
		this.type = 2, this._$AH = b, this._$AN = void 0, this._$AA = e, this._$AB = t, this._$AM = n, this.options = r, this._$Cv = r?.isConnected ?? !0;
	}
	get parentNode() {
		let e = this._$AA.parentNode, t = this._$AM;
		return t !== void 0 && e?.nodeType === 11 && (e = t.parentNode), e;
	}
	get startNode() {
		return this._$AA;
	}
	get endNode() {
		return this._$AB;
	}
	_$AI(e, t = this) {
		e = je(this, e, t), _e(e) ? e === b || e == null || e === "" ? (this._$AH !== b && this._$AR(), this._$AH = b) : e !== this._$AH && e !== y && this._(e) : e._$litType$ === void 0 ? e.nodeType === void 0 ? ye(e) ? this.k(e) : this._(e) : this.T(e) : this.$(e);
	}
	O(e) {
		return this._$AA.parentNode.insertBefore(e, this._$AB);
	}
	T(e) {
		this._$AH !== e && (this._$AR(), this._$AH = this.O(e));
	}
	_(e) {
		this._$AH !== b && _e(this._$AH) ? this._$AA.nextSibling.data = e : this.T(g.createTextNode(e)), this._$AH = e;
	}
	$(e) {
		let { values: t, _$litType$: n } = e, r = typeof n == "number" ? this._$AC(e) : (n.el === void 0 && (n.el = Ae.createElement(Oe(n.h, n.h[0]), this.options)), n);
		if (this._$AH?._$AD === r) this._$AH.p(t);
		else {
			let e = new Me(r, this), n = e.u(this.options);
			e.p(t), this.T(n), this._$AH = e;
		}
	}
	_$AC(e) {
		let t = De.get(e.strings);
		return t === void 0 && De.set(e.strings, t = new Ae(e)), t;
	}
	k(t) {
		ve(this._$AH) || (this._$AH = [], this._$AR());
		let n = this._$AH, r, i = 0;
		for (let a of t) i === n.length ? n.push(r = new e(this.O(ge()), this.O(ge()), this, this.options)) : r = n[i], r._$AI(a), i++;
		i < n.length && (this._$AR(r && r._$AB.nextSibling, i), n.length = i);
	}
	_$AR(e = this._$AA.nextSibling, t) {
		for (this._$AP?.(!1, !0, t); e !== this._$AB;) {
			let t = ue(e).nextSibling;
			ue(e).remove(), e = t;
		}
	}
	setConnected(e) {
		this._$AM === void 0 && (this._$Cv = e, this._$AP?.(e));
	}
}, Pe = class {
	get tagName() {
		return this.element.tagName;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	constructor(e, t, n, r, i) {
		this.type = 1, this._$AH = b, this._$AN = void 0, this.element = e, this.name = t, this._$AM = r, this.options = i, n.length > 2 || n[0] !== "" || n[1] !== "" ? (this._$AH = Array(n.length - 1).fill(/* @__PURE__ */ new String()), this.strings = n) : this._$AH = b;
	}
	_$AI(e, t = this, n, r) {
		let i = this.strings, a = !1;
		if (i === void 0) e = je(this, e, t, 0), a = !_e(e) || e !== this._$AH && e !== y, a && (this._$AH = e);
		else {
			let r = e, o, s;
			for (e = i[0], o = 0; o < i.length - 1; o++) s = je(this, r[n + o], t, o), s === y && (s = this._$AH[o]), a ||= !_e(s) || s !== this._$AH[o], s === b ? e = b : e !== b && (e += (s ?? "") + i[o + 1]), this._$AH[o] = s;
		}
		a && !r && this.j(e);
	}
	j(e) {
		e === b ? this.element.removeAttribute(this.name) : this.element.setAttribute(this.name, e ?? "");
	}
}, Fe = class extends Pe {
	constructor() {
		super(...arguments), this.type = 3;
	}
	j(e) {
		this.element[this.name] = e === b ? void 0 : e;
	}
}, Ie = class extends Pe {
	constructor() {
		super(...arguments), this.type = 4;
	}
	j(e) {
		this.element.toggleAttribute(this.name, !!e && e !== b);
	}
}, Le = class extends Pe {
	constructor(e, t, n, r, i) {
		super(e, t, n, r, i), this.type = 5;
	}
	_$AI(e, t = this) {
		if ((e = je(this, e, t, 0) ?? b) === y) return;
		let n = this._$AH, r = e === b && n !== b || e.capture !== n.capture || e.once !== n.once || e.passive !== n.passive, i = e !== b && (n === b || r);
		r && this.element.removeEventListener(this.name, this, n), i && this.element.addEventListener(this.name, this, e), this._$AH = e;
	}
	handleEvent(e) {
		typeof this._$AH == "function" ? this._$AH.call(this.options?.host ?? this.element, e) : this._$AH.handleEvent(e);
	}
}, Re = class {
	constructor(e, t, n) {
		this.element = e, this.type = 6, this._$AN = void 0, this._$AM = t, this.options = n;
	}
	get _$AU() {
		return this._$AM._$AU;
	}
	_$AI(e) {
		je(this, e);
	}
}, ze = le.litHtmlPolyfillSupport;
ze?.(Ae, Ne), (le.litHtmlVersions ??= []).push("3.3.3");
var Be = (e, t, n) => {
	let r = n?.renderBefore ?? t, i = r._$litPart$;
	if (i === void 0) {
		let e = n?.renderBefore ?? null;
		r._$litPart$ = i = new Ne(t.insertBefore(ge(), e), e, void 0, n ?? {});
	}
	return i._$AI(e), i;
}, Ve = globalThis, He = class extends m {
	constructor() {
		super(...arguments), this.renderOptions = { host: this }, this._$Do = void 0;
	}
	createRenderRoot() {
		let e = super.createRenderRoot();
		return this.renderOptions.renderBefore ??= e.firstChild, e;
	}
	update(e) {
		let t = this.render();
		this.hasUpdated || (this.renderOptions.isConnected = this.isConnected), super.update(e), this._$Do = Be(t, this.renderRoot, this.renderOptions);
	}
	connectedCallback() {
		super.connectedCallback(), this._$Do?.setConnected(!0);
	}
	disconnectedCallback() {
		super.disconnectedCallback(), this._$Do?.setConnected(!1);
	}
	render() {
		return y;
	}
};
He._$litElement$ = !0, He.finalized = !0, Ve.litElementHydrateSupport?.({ LitElement: He });
var Ue = Ve.litElementPolyfillSupport;
Ue?.({ LitElement: He }), (Ve.litElementVersions ??= []).push("4.2.2");
//#endregion
//#region node_modules/@lit/reactive-element/decorators/custom-element.js
var We = (e) => (t, n) => {
	n === void 0 ? customElements.define(e, t) : n.addInitializer(() => {
		customElements.define(e, t);
	});
}, Ge = {
	attribute: !0,
	type: String,
	converter: oe,
	reflect: !1,
	hasChanged: se
}, Ke = (e = Ge, t, n) => {
	let { kind: r, metadata: i } = n, a = globalThis.litPropertyMetadata.get(i);
	if (a === void 0 && globalThis.litPropertyMetadata.set(i, a = /* @__PURE__ */ new Map()), r === "setter" && ((e = Object.create(e)).wrapped = !0), a.set(n.name, e), r === "accessor") {
		let { name: r } = n;
		return {
			set(n) {
				let i = t.get.call(this);
				t.set.call(this, n), this.requestUpdate(r, i, e, !0, n);
			},
			init(t) {
				return t !== void 0 && this.C(r, void 0, e, t), t;
			}
		};
	}
	if (r === "setter") {
		let { name: r } = n;
		return function(n) {
			let i = this[r];
			t.call(this, n), this.requestUpdate(r, i, e, !0, n);
		};
	}
	throw Error("Unsupported decorator location: " + r);
};
function qe(e) {
	return (t, n) => typeof n == "object" ? Ke(e, t, n) : ((e, t, n) => {
		let r = t.hasOwnProperty(n);
		return t.constructor.createProperty(n, e), r ? Object.getOwnPropertyDescriptor(t, n) : void 0;
	})(e, t, n);
}
//#endregion
//#region node_modules/@lit/reactive-element/decorators/state.js
function S(e) {
	return qe({
		...e,
		state: !0,
		attribute: !1
	});
}
//#endregion
//#region node_modules/@lit/reactive-element/decorators/base.js
var Je = (e, t, n) => (n.configurable = !0, n.enumerable = !0, Reflect.decorate && typeof t != "object" && Object.defineProperty(e, t, n), n);
//#endregion
//#region node_modules/@lit/reactive-element/decorators/query.js
function C(e, t) {
	return (n, r, i) => {
		let a = (t) => t.renderRoot?.querySelector(e) ?? null;
		if (t) {
			let { get: e, set: t } = typeof r == "object" ? n : i ?? (() => {
				let e = Symbol();
				return {
					get() {
						return this[e];
					},
					set(t) {
						this[e] = t;
					}
				};
			})();
			return Je(n, r, { get() {
				let n = e.call(this);
				return n === void 0 && (n = a(this), (n !== null || this.hasUpdated) && t.call(this, n)), n;
			} });
		}
		return Je(n, r, { get() {
			return a(this);
		} });
	};
}
//#endregion
//#region node_modules/lit-html/directives/if-defined.js
var Ye = (e) => e ?? b, Xe = "M13,13H11V7H13M13,17H11V15H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", Ze = "M15,20H9V12H4.16L12,4.16L19.84,12H15V20Z", Qe = "M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z", $e = "M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z", et = "M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z", tt = "M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z", nt = "M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z", rt = "M21 11H3V9H21V11M21 13H3V15H21V13Z", it = "M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2M18 20H6V4H13V9H18V20M16 11V18.1L13.9 16L11.1 18.8L8.3 16L11.1 13.2L8.9 11H16Z", at = "M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z", ot = "M21.8,13H20V21H13V17.67L15.79,14.88L16.5,15C17.66,15 18.6,14.06 18.6,12.9C18.6,11.74 17.66,10.8 16.5,10.8A2.1,2.1 0 0,0 14.4,12.9L14.5,13.61L13,15.13V9.65C13.66,9.29 14.1,8.6 14.1,7.8A2.1,2.1 0 0,0 12,5.7A2.1,2.1 0 0,0 9.9,7.8C9.9,8.6 10.34,9.29 11,9.65V15.13L9.5,13.61L9.6,12.9A2.1,2.1 0 0,0 7.5,10.8A2.1,2.1 0 0,0 5.4,12.9A2.1,2.1 0 0,0 7.5,15L8.21,14.88L11,17.67V21H4V13H2.25C1.83,13 1.42,13 1.42,12.79C1.43,12.57 1.85,12.15 2.28,11.72L11,3C11.33,2.67 11.67,2.33 12,2.33C12.33,2.33 12.67,2.67 13,3L17,7V6H19V9L21.78,11.78C22.18,12.18 22.59,12.59 22.6,12.8C22.6,13 22.2,13 21.8,13M7.5,12A0.9,0.9 0 0,1 8.4,12.9A0.9,0.9 0 0,1 7.5,13.8A0.9,0.9 0 0,1 6.6,12.9A0.9,0.9 0 0,1 7.5,12M16.5,12C17,12 17.4,12.4 17.4,12.9C17.4,13.4 17,13.8 16.5,13.8A0.9,0.9 0 0,1 15.6,12.9A0.9,0.9 0 0,1 16.5,12M12,6.9C12.5,6.9 12.9,7.3 12.9,7.8C12.9,8.3 12.5,8.7 12,8.7C11.5,8.7 11.1,8.3 11.1,7.8C11.1,7.3 11.5,6.9 12,6.9Z", st = "M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z", ct = "M12 2C7.04 2 3 6.04 3 11C3 14.91 5.5 18.24 9 19.47V22H11V19.94C11.33 20 11.66 20 12 20S12.67 20 13 19.94V22H15V19.47C18.5 18.23 21 14.9 21 11C21 6.04 16.96 2 12 2M14.25 14L11.25 17L9.75 15.5L11 14.25L9.75 13L12.75 10L14.25 11.5L13 12.75L14.25 14M16 9H8V7H16V9Z", lt = "M17,13H7V11H17M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z", ut = "M16,7V3H14V7H10V3H8V7H8C7,7 6,8 6,9V14.5L9.5,18V21H14.5V18L18,14.5V9C18,8 17,7 16,7Z", dt = "M20.84 22.73L15.31 17.2L14.5 18V21H9.5V18L6 14.5V9C6 8.7 6.1 8.41 6.25 8.14L1.11 3L2.39 1.73L22.11 21.46L20.84 22.73M18 14.5V9C18 8 17 7 16 7V3H14V7H10.2L17.85 14.65L18 14.5M10 3H8V4.8L10 6.8V3Z", ft = "M16 7V3H14V7H10V3H8V7C7 7 6 8 6 9V14.5L9.5 18V21H14.5V18L18 14.5V9C18 8 17 7 16 7M16 13.67L13.09 16.59L12.67 17H11.33L10.92 16.59L8 13.67V9.09C8 9.06 8.06 9 8.09 9H15.92C15.95 9 16 9.06 16 9.09V13.67Z", pt = "M4.22,2A2.22,2.22 0 0,0 2,4.22V19.78C2,21 3,22 4.22,22H19.78A2.22,2.22 0 0,0 22,19.78V4.22C22,3 21,2 19.78,2H4.22M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M8.27,7.54L6.27,11L8,12L10,8.54L8.27,7.54M15.73,7.54L14,8.54L16,12L17.73,11L15.73,7.54M11,14V18H13V14H11Z", mt = "M19.78 2H4.22C3 2 2 3 2 4.22V19.78C2 21 3 22 4.22 22H19.78C21 22 22 21 22 19.78V4.22C22 3 21 2 19.78 2M20 13L16.55 16.45C16.19 16.81 15.75 17 15.3 17H8.7C8.25 17 7.81 16.81 7.45 16.45L4 13C3.5 12.5 3.5 11.5 4 11L7.45 7.55C7.81 7.19 8.25 7 8.7 7H15.3C15.75 7 16.19 7.19 16.55 7.55L20 11C20.5 11.5 20.5 12.5 20 13M10.5 14C10.5 13.17 11.17 12.5 12 12.5S13.5 13.17 13.5 14 12.83 15.5 12 15.5 10.5 14.83 10.5 14M15.5 12C15.5 11.17 16.17 10.5 17 10.5S18.5 11.17 18.5 12 17.83 13.5 17 13.5 15.5 12.83 15.5 12M5.5 12C5.5 11.17 6.17 10.5 7 10.5S8.5 11.17 8.5 12 7.83 13.5 7 13.5 5.5 12.83 5.5 12Z", ht = "M4.22 2A2.22 2.22 0 0 0 2 4.22V19.78C2 21 3 22 4.22 22H19.78A2.22 2.22 0 0 0 22 19.78V4.22C22 3 21 2 19.78 2H4.22M11 4.07V6H13V4.07A8 8 0 0 1 20 12A8 8 0 0 1 13 19.93V18H11V19.93A8 8 0 0 1 4 12A8 8 0 0 1 11 4.07M7.5 10.5A1.5 1.5 0 0 0 6 12C6 12.83 6.66 13.5 7.5 13.5A1.5 1.5 0 0 0 9 12A1.5 1.5 0 0 0 7.5 10.5M16.5 10.5A1.5 1.5 0 0 0 15 12A1.5 1.5 0 0 0 16.5 13.5A1.5 1.5 0 0 0 18 12A1.5 1.5 0 0 0 16.5 10.5Z", gt = "M7.5,10.5A1.5,1.5 0 0,1 9,12A1.5,1.5 0 0,1 7.5,13.5C6.66,13.5 6,12.83 6,12A1.5,1.5 0 0,1 7.5,10.5M16.5,10.5A1.5,1.5 0 0,1 18,12A1.5,1.5 0 0,1 16.5,13.5A1.5,1.5 0 0,1 15,12A1.5,1.5 0 0,1 16.5,10.5M4.22,2H19.78C21,2 22,3 22,4.22V19.78A2.22,2.22 0 0,1 19.78,22H4.22C3,22 2,21 2,19.78V4.22A2.22,2.22 0 0,1 4.22,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4Z", _t = "M4.22 2A2.22 2.22 0 0 0 2 4.22V19.78C2 21 3 22 4.22 22H19.78A2.22 2.22 0 0 0 22 19.78V4.22C22 3 21 2 19.78 2H4.22M12 4A8 8 0 0 1 20 12A8 8 0 0 1 12 20A8 8 0 0 1 4 12A8 8 0 0 1 12 4M12 6A1.5 1.5 0 0 0 10.5 7.5A1.5 1.5 0 0 0 12 9A1.5 1.5 0 0 0 13.5 7.5A1.5 1.5 0 0 0 12 6M7.5 10.5A1.5 1.5 0 0 0 6 12C6 12.83 6.66 13.5 7.5 13.5A1.5 1.5 0 0 0 9 12A1.5 1.5 0 0 0 7.5 10.5M16.5 10.5A1.5 1.5 0 0 0 15 12A1.5 1.5 0 0 0 16.5 13.5A1.5 1.5 0 0 0 18 12A1.5 1.5 0 0 0 16.5 10.5Z", vt = "M10.5 16.5C10.5 15.68 11.17 15 12 15C12.83 15 13.5 15.68 13.5 16.5C13.5 17.34 12.83 18 12 18C11.17 18 10.5 17.34 10.5 16.5M10.5 7.5C10.5 6.67 11.17 6 12 6C12.83 6 13.5 6.67 13.5 7.5C13.5 8.33 12.83 9 12 9C11.17 9 10.5 8.33 10.5 7.5M4.22 2H19.78C21 2 22 3 22 4.22V19.78C22 21 21 22 19.78 22H4.22C3 22 2 21 2 19.78V4.22C2 3 3 2 4.22 2M12 4C7.58 4 4 7.58 4 12C4 16.42 7.58 20 12 20C16.42 20 20 16.42 20 12C20 7.58 16.42 4 12 4M10.5 12C10.5 11.17 11.17 10.5 12 10.5C12.83 10.5 13.5 11.17 13.5 12C13.5 12.83 12.83 13.5 12 13.5C11.17 13.5 10.5 12.83 10.5 12Z", yt = "M10 9.5V14.5H8V9.5M19.78 2C21 2 22 3 22 4.22V19.78C22 21 21 22 19.78 22H4.22C3 22 2 21 2 19.78V4.22C2 3 3 2 4.22 2M12 4C7.58 4 4 7.58 4 12C4 16.42 7.58 20 12 20C16.42 20 20 16.42 20 12C20 7.58 16.42 4 12 4M16 9.5V14.5H14V9.5Z", bt = "M4 2A2 2 0 0 0 2 4V20A2 2 0 0 0 4 22H20A2 2 0 0 0 22 20V4A2 2 0 0 0 20 2H4M4 4H20V20H4V4M11 7V11H13V7H11M6 14.75V17H9.5V14.75H6M14.5 14.75V17H18V14.75H14.5Z", xt = "M8,7H10V12H8V7M4.22,2H19.78C21,2 22,3 22,4.22V19.78A2.22,2.22 0 0,1 19.78,22H4.22C3,22 2,21 2,19.78V4.22A2.22,2.22 0 0,1 4.22,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M14,7.5H16V11.5H14V7.5M10.5,16.25A1.5,1.5 0 0,1 12,14.75A1.5,1.5 0 0,1 13.5,16.25V17H10.5V16.25Z", St = "M13,14C9.64,14 8.54,15.35 8.18,16.24C9.25,16.7 10,17.76 10,19A3,3 0 0,1 7,22A3,3 0 0,1 4,19C4,17.69 4.83,16.58 6,16.17V7.83C4.83,7.42 4,6.31 4,5A3,3 0 0,1 7,2A3,3 0 0,1 10,5C10,6.31 9.17,7.42 8,7.83V13.12C8.88,12.47 10.16,12 12,12C14.67,12 15.56,10.66 15.85,9.77C14.77,9.32 14,8.25 14,7A3,3 0 0,1 17,4A3,3 0 0,1 20,7C20,8.34 19.12,9.5 17.91,9.86C17.65,11.29 16.68,14 13,14M7,18A1,1 0 0,0 6,19A1,1 0 0,0 7,20A1,1 0 0,0 8,19A1,1 0 0,0 7,18M7,4A1,1 0 0,0 6,5A1,1 0 0,0 7,6A1,1 0 0,0 8,5A1,1 0 0,0 7,4M17,6A1,1 0 0,0 16,7A1,1 0 0,0 17,8A1,1 0 0,0 18,7A1,1 0 0,0 17,6Z", Ct = "M17 6H7C3.69 6 1 8.69 1 12S3.69 18 7 18H17C20.31 18 23 15.31 23 12S20.31 6 17 6M17 16H7C4.79 16 3 14.21 3 12S4.79 8 7 8H17C19.21 8 21 9.79 21 12S19.21 16 17 16M17 9C15.34 9 14 10.34 14 12S15.34 15 17 15 20 13.66 20 12 18.66 9 17 9Z", wt = "M21.71 20.29L20.29 21.71A1 1 0 0 1 18.88 21.71L7 9.85A3.81 3.81 0 0 1 6 10A4 4 0 0 1 2.22 4.7L4.76 7.24L5.29 6.71L6.71 5.29L7.24 4.76L4.7 2.22A4 4 0 0 1 10 6A3.81 3.81 0 0 1 9.85 7L21.71 18.88A1 1 0 0 1 21.71 20.29M2.29 18.88A1 1 0 0 0 2.29 20.29L3.71 21.71A1 1 0 0 0 5.12 21.71L10.59 16.25L7.76 13.42M20 2L16 4V6L13.83 8.17L15.83 10.17L18 8H20L22 4Z", Tt = "M9,3V4H4V6H5V19A2,2 0 0,0 7,21H17A2,2 0 0,0 19,19V6H20V4H15V3H9M7,6H17V19H7V6M9,8V17H11V8H9M13,8V17H15V8H13Z", Et = "M2 12H4V17H20V12H22V17C22 18.11 21.11 19 20 19H4C2.9 19 2 18.11 2 17V12M12 2L6.46 7.46L7.88 8.88L11 5.75V15H13V5.75L16.13 8.88L17.55 7.45L12 2Z", Dt = "M16 10H8V8H16M2 17A2 2 0 0 0 4 19H20A2 2 0 0 0 22 17V12H20V17H4V12H2Z", Ot = "M2 12H4V17H20V12H22V17A2 2 0 0 1 20 19H4A2 2 0 0 1 2 17M11 5H13V8H16V10H13V13H11V10H8V8H11Z", kt = "M2 17A2 2 0 0 0 4 19H20A2 2 0 0 0 22 17V12H20V17H4V12H2M14.12 5.46L15.54 6.88L13.41 9L15.54 11.12L14.12 12.54L12 10.41L9.88 12.54L8.46 11.12L10.59 9L8.46 6.88L9.88 5.46L12 7.59Z", At = [{
	value: "markdown",
	label: "Markdown"
}, {
	value: "json",
	label: "JSON"
}], jt = {
	markdown: "text/markdown;charset=utf-8",
	json: "application/json;charset=utf-8"
}, Mt = () => ({
	format: "markdown",
	includeHistory: !1,
	saving: !1,
	error: null
}), Nt = (e, t) => e ? {
	...e,
	...t
} : null, Pt = (e) => ({
	type: "outlet_binder/export",
	format: e.format,
	include_history: e.includeHistory
}), Ft = (e) => e === 0 ? null : `${e} staged ${e === 1 ? "change is" : "changes are"} not in the file. It shows what has been committed.`, It = (e, t) => {
	let n = URL.createObjectURL(new Blob([e.content], { type: jt[t] })), r = document.createElement("a");
	r.href = n, r.download = e.filename, document.body.append(r), r.click(), r.remove(), URL.revokeObjectURL(n);
}, w = {
	primaryText: {
		light: "#141414",
		dark: "#e1e1e1"
	},
	secondaryText: {
		light: "#5e5e5e",
		dark: "#9b9b9b"
	},
	disabledText: {
		light: "#bdbdbd",
		dark: "#6f6f6f"
	},
	accent: {
		light: "#009ac7",
		dark: "#009ac7"
	},
	error: {
		light: "#db4437",
		dark: "#db4437"
	},
	warning: {
		light: "#ffa600",
		dark: "#ffa600"
	},
	pageBackground: {
		light: "#fafafa",
		dark: "#111111"
	},
	cardBackground: {
		light: "#ffffff",
		dark: "#1c1c1c"
	},
	obElementName: {
		light: "#6c85a3",
		dark: "#6c85a3"
	},
	buildStamp: {
		light: "#b58900",
		dark: "#ffe082"
	},
	onAccent: {
		light: "#ffffff",
		dark: "#ffffff"
	},
	hoverBox: {
		light: "#2b2f33",
		dark: "#dfe2e5"
	},
	hoverData: {
		light: "#b8bec4",
		dark: "#4a5057"
	},
	hoverTitle: {
		light: "#ffffff",
		dark: "#14171a"
	},
	hoverStop: {
		light: "#ff6b5e",
		dark: "#d93025"
	}
}, T = (e) => `${e / 16}rem`, Lt = {
	fontFamily: "Roboto, sans-serif",
	fontSize: T(14),
	fontWeight: 400,
	color: w.primaryText,
	fontStyle: "normal",
	textAlign: "start"
}, Rt = {
	"ob-element-name": { changes: { color: w.obElementName } },
	"small-text": { changes: { fontSize: T(12) } },
	"tiny-text": { changes: { fontSize: T(10) } },
	"supporting-text": { changes: { color: w.secondaryText } },
	"error-text": { changes: { color: w.error } },
	"warning-text": { changes: { color: w.warning } },
	"disabled-text": { changes: { color: w.disabledText } },
	emphasis: { changes: { fontWeight: 700 } },
	"italic-text": { changes: { fontStyle: "italic" } },
	medium: { changes: { fontWeight: 500 } },
	"strong-hover-text": { changes: { color: w.hoverTitle } },
	"text-on-fill": { changes: { color: w.onAccent } }
}, zt = {
	"hover-text": { fontSize: "0.85em" },
	"clickable-outline": { outline: 40 },
	"strike-through": { strikeThrough: !0 }
};
Object.keys(Rt), Object.keys(zt);
var E = {
	"page-title": {
		parent: "base",
		changes: { fontSize: T(20) }
	},
	"heading-text": {
		parent: "base",
		changes: { fontSize: T(16) },
		family: !0
	},
	heading: {
		parent: "heading-text",
		changes: {},
		adds: ["medium"]
	},
	"tab-label": {
		parent: "heading-text",
		changes: {},
		adds: ["medium"],
		states: {
			hover: { color: w.accent },
			selected: {
				color: w.accent,
				underline: w.accent
			}
		},
		underlineWidth: T(2)
	},
	"table-division-heading": {
		parent: "heading-text",
		changes: {}
	},
	"dialog-title": {
		parent: "heading",
		changes: {}
	},
	"dialog-section": {
		parent: "heading",
		changes: {},
		adds: ["ob-element-name"]
	},
	"dialog-field-prompt": {
		parent: "base",
		changes: {},
		adds: ["ob-element-name", "small-text"]
	},
	"dialog-field-note": {
		parent: "base",
		changes: {},
		adds: ["supporting-text", "small-text"]
	},
	"column-heading": {
		parent: "base",
		changes: {},
		adds: ["supporting-text", "emphasis"]
	},
	"dialog-metadata": {
		parent: "dialog-field-note",
		changes: { fontFamily: "monospace" },
		adds: ["tiny-text"]
	},
	hover: {
		parent: "base",
		changes: {},
		adds: ["hover-text"],
		family: !0
	},
	"hover-title": {
		parent: "hover",
		changes: {},
		adds: ["strong-hover-text", "emphasis"]
	},
	"hover-data": {
		parent: "hover",
		changes: { color: w.hoverData }
	},
	"hover-prompt": {
		parent: "hover",
		changes: { textAlign: "end" },
		adds: ["ob-element-name", "emphasis"]
	},
	"badge-text": {
		parent: "base",
		changes: { fontSize: T(9) },
		adds: ["emphasis"],
		family: !0,
		provisional: !0
	},
	"debug-badge-text": {
		parent: "badge-text",
		changes: { letterSpacing: "0.04em" },
		adds: ["error-text"],
		provisional: !0
	},
	"new-badge-text": {
		parent: "badge-text",
		changes: { lineHeight: 1.5 },
		adds: ["text-on-fill"],
		provisional: !0
	},
	"pending-marker": {
		parent: "base",
		changes: { color: w.accent },
		adds: ["emphasis"],
		provisional: !0
	},
	"debug-delete-label": {
		parent: "base",
		changes: { lineHeight: 1.3 },
		states: { hover: { color: w.onAccent } },
		adds: ["small-text", "error-text"],
		provisional: !0
	},
	"build-stamp": {
		parent: "base",
		changes: { color: w.buildStamp }
	},
	"info-cue": {
		parent: "base",
		changes: {
			fontFamily: "Georgia, serif",
			fontStyle: "italic"
		},
		states: { hover: { color: w.primaryText } },
		adds: [
			"tiny-text",
			"supporting-text",
			"emphasis"
		],
		provisional: !0
	},
	"hover-action": {
		parent: "hover",
		changes: {},
		adds: ["strong-hover-text"],
		provisional: !0
	}
};
Object.keys(E).filter((e) => E[e].family === !0), Object.keys(E).filter((e) => E[e].provisional === !0);
var Bt = ["base", ...Object.keys(E)], Vt = (e) => `ts-${e}`, Ht = (e, t) => {
	let n = [], r = /* @__PURE__ */ new Set(), i = t;
	for (; i !== "base";) {
		if (r.has(i)) throw Error(`text style "${t}" has a cycle through "${i}"`);
		if (r.add(i), !Object.hasOwn(e, i)) throw Error(`text style "${i}" is not defined`);
		let a = e[i];
		n.unshift(a), i = a.parent;
	}
	return n;
}, Ut = (e, t) => Ht(e, t).flatMap((e) => [...e.adds ?? []]), D = (e, ...t) => [.../* @__PURE__ */ new Set([
	e,
	...Ut(E, e),
	...t
])].map(Vt).join(" "), O = (...e) => e.map(Vt).join(" "), Wt = (e, t) => Ht(e, t).reduce((e, t) => ({
	...e,
	...t.changes
}), Lt), Gt = (e, t) => new Set(Ht(e, t).flatMap((e) => Object.keys(e.changes))), Kt = ":host", qt = (e) => [
	...e.fontFamily === void 0 ? [] : [`font-family: ${e.fontFamily};`],
	...e.fontSize === void 0 ? [] : [`font-size: ${e.fontSize};`],
	...e.fontWeight === void 0 ? [] : [`font-weight: ${e.fontWeight};`],
	...e.color === void 0 ? [] : [`color: ${e.color.light};`],
	...e.fontStyle === void 0 ? [] : [`font-style: ${e.fontStyle};`],
	...e.textAlign === void 0 ? [] : [`text-align: ${e.textAlign};`],
	...e.lineHeight === void 0 ? [] : [`line-height: ${e.lineHeight};`],
	...e.letterSpacing === void 0 ? [] : [`letter-spacing: ${e.letterSpacing};`]
], Jt = (e, t) => [`color: ${e.color[t]};`, ...e.underline === void 0 ? [] : [`border-bottom-color: ${e.underline[t]};`]], Yt = (e, t) => e === void 0 ? [] : [{
	selectors: t,
	light: Jt(e, "light"),
	dark: Jt(e, "dark")
}], Xt = (e, t) => {
	let n = Wt(e, t), r = Gt(e, t);
	return {
		...n,
		fontStyle: r.has("fontStyle") ? n.fontStyle : void 0,
		textAlign: r.has("textAlign") ? n.textAlign : void 0
	};
}, Zt = (e) => Bt.flatMap((t) => {
	let n = Wt(e, t), r = `.${Vt(t)}`, i = t === "base" ? void 0 : e[t], a = i?.underlineWidth;
	return [
		{
			selectors: t === "base" ? [Kt, r] : [r],
			light: [...qt(Xt(e, t)), ...a === void 0 ? [] : [`border-bottom: ${a} solid transparent;`]],
			dark: [`color: ${n.color.dark};`]
		},
		...Yt(i?.states?.hover, [`${r}:hover`, `${r}:focus-visible`]),
		...Yt(i?.states?.selected, [`${r}[aria-selected="true"]`])
	];
}), Qt = (e) => Object.keys(e).map((t) => {
	let { changes: n } = e[t];
	return {
		selectors: [`.${Vt(t)}`],
		light: qt(n),
		dark: n.color === void 0 ? [] : [`color: ${n.color.dark};`]
	};
}), $t = (e) => "outline" in e ? `border-color: color-mix(in srgb, currentColor ${e.outline}%, transparent);` : "strikeThrough" in e ? "text-decoration: line-through;" : `font-size: ${e.fontSize};`, en = (e) => Object.keys(e).map((t) => ({
	selectors: [`.${Vt(t)}`],
	light: [$t(e[t])],
	dark: []
})), tn = (e) => e === Kt ? ":host(:not([data-theme=\"light\"]))" : `:host(:not([data-theme="light"])) ${e}`, nn = (e) => e === Kt ? ":host([data-theme=\"dark\"])" : `:host([data-theme="dark"]) ${e}`, rn = (e, t) => `${e.join(",\n")} {\n  ${t.join("\n  ")}\n}`, an = (e) => {
	let t = e.map((e) => rn(e.selectors, e.light)), n = (t) => e.filter((e) => e.dark.length > 0).map((e) => rn(e.selectors.map(t), e.dark));
	return [
		...t,
		`@media (prefers-color-scheme: dark) {\n${n(tn).join("\n")}\n}`,
		...n(nn)
	].join("\n");
}, on = (e, t = Rt, n = zt) => an([
	...Zt(e),
	...Qt(t),
	...en(n)
]), sn = () => on(E), cn = (e, t) => e ? t : null, k = (e, t) => v`<p class="dialog-title ${D("dialog-title")}">${e}${t === null ? b : v` <span class="build-stamp ${D("build-stamp")}">${t}</span>`}</p>`, ln = {
	"hover-box": {
		background: w.hoverBox,
		color: w.hoverData,
		radius: "6px",
		shadow: "0 2px 12px rgba(0, 0, 0, 0.35)",
		vars: { "--tip-stop": w.hoverStop }
	},
	"modal-dialog-box": {
		background: {
			light: "#ffffff",
			dark: "rgba(255, 255, 255, 0.12)"
		},
		radius: "8px",
		shadow: "0 4px 24px rgba(0, 0, 0, 0.2)",
		color: w.primaryText,
		border: {
			light: "none",
			dark: "1px solid rgba(255, 255, 255, 0.18)"
		},
		blur: "14px",
		backdrop: "rgba(0, 0, 0, 0.4)"
	}
};
Object.keys(ln);
var A = (e) => `sf-${e}`, un = (e, t) => [
	`background: ${e.background[t]};`,
	...e.color === void 0 ? [] : [`color: ${e.color[t]};`],
	...t === "light" ? [`border-radius: ${e.radius};`, `box-shadow: ${e.shadow};`] : [],
	...e.border === void 0 ? [] : [`border: ${e.border[t]};`],
	...t === "dark" && e.blur !== void 0 ? [`-webkit-backdrop-filter: blur(${e.blur});`, `backdrop-filter: blur(${e.blur});`] : [],
	...Object.entries(e.vars ?? {}).map(([e, n]) => `${e}: ${n[t]};`)
], dn = (e) => Object.keys(e).flatMap((t) => {
	let n = e[t], r = `.${A(t)}`;
	return [{
		selectors: [r],
		light: un(n, "light"),
		dark: un(n, "dark")
	}, ...n.backdrop === void 0 ? [] : [{
		selectors: [`${r}::backdrop`],
		light: [`background: ${n.backdrop};`],
		dark: []
	}]];
}), fn = (e) => an(dn(e)), pn = () => fn(ln);
//#endregion
//#region src/outlet-binder-panel/export-view.ts
function mn(e, t, n, r) {
	return e ? v`
    <dialog
      class="export-dialog ${A("modal-dialog-box")}"
      @close=${() => n.close()}
      @cancel=${(e) => n.cancel(e)}
    >
      <div class="dialog-body">
        ${k("Export the current state", r)}
        <fieldset class="export-formats" ?disabled=${e.saving}>
          <legend class=${D("dialog-field-prompt")}>Format</legend>
          ${At.map((t) => v`
              <label class="choice-row">
                <input
                  type="radio"
                  name="export-format"
                  value=${t.value}
                  .checked=${t.value === e.format}
                  @change=${() => n.setFormat(t.value)}
                />
                ${t.label}
              </label>
            `)}
        </fieldset>
        <label class="choice-row">
          <input
            type="checkbox"
            .checked=${e.includeHistory}
            ?disabled=${e.saving}
            @change=${(e) => n.setIncludeHistory(e.target.checked)}
          />
          Include Plugged Into history
        </label>
        ${t ? v`<p class="export-notice ${O("supporting-text")}">${t}</p>` : ""}
        ${e.error ? v`<p class="error ${O("error-text")}">${e.error}</p>` : ""}
      </div>
      <div class="dialog-actions">
        <button ?disabled=${e.saving} @click=${() => n.close()}>Cancel</button>
        <button class="go" ?disabled=${e.saving} @click=${() => n.run()}>
          ${e.saving ? "Exporting…" : "Download"}
        </button>
      </div>
    </dialog>
  ` : v`<dialog class="export-dialog ${A("modal-dialog-box")}" @close=${() => n.close()}></dialog>`;
}
//#endregion
//#region src/outlet-binder-panel/control-styles.ts
var hn = {
	plainText: {
		light: "#009ac7",
		dark: "#37c8fd"
	},
	plainHover: {
		light: "#dff3fc",
		dark: "#002e3e"
	},
	main: {
		light: "#009ac7",
		dark: "#009ac7"
	},
	mainHover: {
		light: "#006787",
		dark: "#006787"
	},
	danger: {
		light: "#dc3146",
		dark: "#b30532"
	},
	dangerHover: {
		light: "#b30532",
		dark: "#8a132c"
	},
	go: {
		light: "#00883c",
		dark: "#036730"
	},
	goHover: {
		light: "#036730",
		dark: "#0a5027"
	},
	disabledFill: {
		light: "#cccccc",
		dark: "#4a4a4a"
	},
	disabledText: {
		light: "#f3f3f3",
		dark: "#7a7a7a"
	},
	goText: {
		light: "#036730",
		dark: "#00ac49"
	},
	dangerText: {
		light: "#b30532",
		dark: "#f3676c"
	},
	disabledQuiet: {
		light: "#b1b1b1",
		dark: "#7a7a7a"
	},
	onFill: {
		light: "#ffffff",
		dark: "#ffffff"
	},
	iconHover: {
		light: "rgba(0, 0, 0, 0.08)",
		dark: "rgba(255, 255, 255, 0.12)"
	}
};
Object.keys(hn);
var gn = (e) => `--ob-btn-${e.replace(/[A-Z]/g, (e) => `-${e.toLowerCase()}`)}`, _n = {
	linked: w.error,
	plug: w.accent,
	unavailable: w.disabledText,
	quiet: w.secondaryText
};
Object.keys(_n);
var vn = (e) => `--ob-icon-${e.replace(/[A-Z]/g, (e) => `-${e.toLowerCase()}`)}`, yn = {
	hoverColor: hn.plainText,
	wash: {
		hover: 12,
		pressed: 18
	},
	room: {
		block: "3px",
		inline: "2px"
	},
	radius: "5px",
	border: "1px"
}, bn = () => "ct-clickable", xn = (e) => `background: color-mix(in srgb, currentColor ${e}%, transparent);`, Sn = a(`${pn()}\n${`${((e = hn) => {
	let t = Object.entries(e), n = (e) => t.map(([t, n]) => `${gn(t)}: ${n[e]};`);
	return an([{
		selectors: [":host"],
		light: n("light"),
		dark: n("dark")
	}]);
})()}\n${((e = _n) => {
	let t = Object.entries(e), n = (e) => t.map(([t, n]) => `${vn(t)}: ${n[e]};`);
	return an([{
		selectors: [":host"],
		light: n("light"),
		dark: n("dark")
	}]);
})()}\n${((e = yn) => {
	let t = `.${bn()}`, n = (t) => `-${parseFloat(t) + parseFloat(e.border)}px`;
	return `${[
		`${t} {`,
		`  border: ${e.border} solid transparent;`,
		"  background: none;",
		`  padding: ${e.room.block} ${e.room.inline};`,
		`  margin: ${n(e.room.block)} ${n(e.room.inline)};`,
		`  border-radius: ${e.radius};`,
		"  font: inherit;",
		"  color: inherit;",
		"  text-align: inherit;",
		"  cursor: pointer;",
		"}",
		`${t}:hover,\n${t}:focus-visible {`,
		`  ${xn(e.wash.hover)}`,
		"}",
		`${t}:active {`,
		`  ${xn(e.wash.pressed)}`,
		"}"
	].join("\n")}\n${an([{
		selectors: [
			`${t}:hover`,
			`${t}:focus-visible`,
			`${t}:active`
		],
		light: [`color: ${e.hoverColor.light};`],
		dark: [`color: ${e.hoverColor.dark};`]
	}])}`;
})()}`}\n${sn()}`), Cn = o`
  :host {
    display: flex;
    flex-direction: column;
    height: 100vh;
    box-sizing: border-box;
    padding: 24px;
    color-scheme: light dark;
    background: #fff;
    /* Floor, not a true sync -- the three .structured-table elements are
       independent tables (#130), so their thead rows can't share a real
       height. Read by .th-stack/.th-row (below, on the <th>'s own direct
       wrapper <div>, not the <th> itself -- min-height set directly on a
       sticky <th> has zero effect on this table's auto layout), sized to the
       co-table's naturally-taller two-line header (.th-stack, about 48px), so
       the isolated tables' plain one-line header (New button only, about 29px)
       grows to meet it instead of leaving their "Isolated - N" band sitting
       higher than the co-table's own first section-header row. rem, not px --
       an accessibility root-font-size preference (not the same as ordinary
       browser page zoom, which scales px/rem alike) only scales rem/em, so a
       px floor would ignore it entirely; see the .link-btn font-size comment
       elsewhere in this file for the same reasoning. If the co-table's own
       header ever grows past this (longer label text, a bumped root font
       size), the two drift apart -- not handled, since nothing today does. */
    --structured-header-min-height: 3.25rem;
    /* Column-linking tint (#167): a low-alpha background painted on the
       Appliances/Unmanaged Outlets tables and co-table columns, sitting
       behind any row/cell that already sets its own background
       (.row-shade, tr.section-header's blue tints, the sticky thead) --
       those simply paint over it in normal DOM stacking order, no
       special CSS needed for that layering. Bumped up in dark mode
       (below) since the same alpha reads as barely-there against
       #1c1c1c; light-mode values are the default here. */
    --column-tint-appliance: rgba(76, 175, 80, 0.08);
    --column-tint-uo: rgba(121, 85, 72, 0.08);
    /* The button colours, --ob-btn-*, are generated into :host in light and
       dark from BUTTON_COLOURS (control-styles.ts); the rules here read them. */
  }
  .header-bar {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    padding-bottom: 16px;
  }
  .header-bar h1 {
    margin: 0;
  }
  /* Global debug-mode indicator (#292), the header-level counterpart to the
     debug-delete-btn. Reuses that control's error-color/dashed signifier
     rather than .new-badge's primary-color -- both announce the same
     condition (destructive per-row deletes are exposed), so they should read
     as one family. Pill shape borrowed from .new-badge since this sits
     beside heading text rather than acting as a button. */
  .debug-mode-badge {
    display: inline-block;
    margin-right: 10px;
    padding: 1px 7px;
    border: 1px dashed var(--error-color, #b00020);
    border-radius: 8px;
    vertical-align: middle;
  }
  /* The header-bar's right side: the hamburger menu (#403), the permanent,
     always-right-most entry point under justify-content: space-between. The
     theme select lives in the Settings dialog the menu's last entry opens,
     and the region select in the Configure dialog's options flow. */
  .header-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  /* The main-screen filter's pop-over (#529): the menu's own box (.menu-list,
     so it is frosted in dark mode alike), holding the dialogs' filter input
     and a close button on one row, under a drag handle. Its wrapper is not a .menu-wrap: the
     menu treats a click inside any .menu-wrap as a click inside the menu. The browser's own search-field clear
     button is hidden: closing is what clears. */
  .main-filter:not([hidden]) {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  /* The drag handle: a grip strip along the top. touch-action: none, so a
     finger dragging it moves the pop-over rather than scrolling the page. */
  .main-filter-handle {
    display: flex;
    justify-content: center;
    cursor: move;
    touch-action: none;
    user-select: none;
    --ob-icon-colour: var(--ob-icon-quiet);
  }
  .main-filter-handle .menu-entry-icon {
    fill: var(--ob-icon-colour);
  }
  .main-filter-row {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .main-filter-input {
    flex: 1 1 auto;
    min-width: 0;
  }
  .main-filter-input::-webkit-search-cancel-button {
    -webkit-appearance: none;
    appearance: none;
  }
  .main-filter-close {
    flex: none;
    border: none;
    background: none;
    padding: 0;
    min-width: 36px;
    min-height: 36px;
    border-radius: 50%;
    transition: background-color 0.15s ease-out;
    cursor: pointer;
    color: inherit;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  /* #311: the session toolbar's own row, centred below the title. A
     sibling of .header-bar and .scroll-region (outside the scroll
     container), so it stays pinned with the header exactly as the header
     does. The row only exists in the DOM while something is staged, so it
     takes no height otherwise -- content moves down by one row when the
     first change is staged, and back up after Commit or Flush. */
  .toolbar-row {
    flex: 0 0 auto;
    display: flex;
    justify-content: center;
    padding-bottom: 16px;
  }
  /* #290: the medium tier's tab row -- a sibling of .toolbar-row and
     .scroll-region, so it stays pinned under the title and toolbar the
     same way they do. Underline tabs, as in HA's own settings pages: plain
     text on one full-width divider line sitting directly on the table, the
     selected tab marked by a thick primary-colour underline. Pill-shaped
     .session-btn tabs were tried first and rejected live -- they read as
     more buttons and didn't connect to the table below. Text and line
     colours are the table headings' own pair, so dark mode needs nothing
     extra. */
  .tab-row {
    flex: 0 0 auto;
    display: flex;
    justify-content: center;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
    /* A gap between the tab line and the table's own header, on every
       tab -- without it the table sits flush on the line (live review). */
    margin-bottom: 8px;
  }
  .tab-btn {
    padding: 8px 16px;
    background: none;
    border: none;
    /* Overlaps the row's own 1px line, so the selected underline (the Tab
       label style's border) sits on it rather than below it. */
    margin-bottom: -1px;
    cursor: pointer;
  }
  /* #320: in the narrow tier the count drops under the name, so three
     labels fit a phone's width on one row. */
  .tab-row.narrow .tab-btn {
    padding: 8px 8px;
  }
  .tab-row.narrow .tab-count,
  .tab-row.narrow .tab-match {
    display: block;
  }
  /* Edit-session toolbar (#190). The group itself always renders in Batch
     mode, and in Immediate mode only when something is staged -- once
     rendered, buttons stay visible and individually disabled rather than
     hidden one at a time. Copies
     .create-btn's look (below) under its own selector: that rule is scoped
     to .structured-table thead, which this toolbar isn't inside. */
  .session-toolbar {
    display: flex;
    gap: 6px;
  }
  .session-btn {
    padding: 2px 9px;
    font: inherit;
    color: var(--ob-btn-plain-text);
    background: none;
    border: 1px solid currentColor;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.15s ease-out;
  }
  /* Outlined, as HA's outlined buttons: hover and focus tint the button in
     its own colour rather than filling it, and only while it is enabled. */
  .session-btn:focus-visible:not(:disabled) {
    background: color-mix(in srgb, currentColor 14%, transparent);
  }
  @media (hover: hover) {
    .session-btn:hover:not(:disabled) {
      background: color-mix(in srgb, currentColor 14%, transparent);
    }
  }
  .session-btn:disabled {
    color: var(--ob-btn-disabled-quiet);
    cursor: default;
  }
  /* Flush is destructive (discards every staged change, #300's confirm
     dialog exists because of it) -- red like .dialog-actions button.danger,
     not the same blue as Undo/Redo, which are reversible. Enabled only, so a
     disabled Flush keeps .session-btn:disabled's grey. */
  .session-btn.danger:not(:disabled) {
    color: var(--ob-btn-danger-text);
  }
  /* Commit is the "go" action -- it writes every staged change for real
     (#301's own confirm dialog exists because of that), so it gets its
     own green, distinct from both Undo/Redo's neutral blue and Flush's
     destructive red -- like .dialog-actions button.go below. Enabled only,
     like Flush. */
  .session-btn.go:not(:disabled) {
    color: var(--ob-btn-go-text);
  }
  /* Batch mode's tray icon (#537), before the label of a toolbar button or
     of a dialog button that stages. It takes the button's text colour, so
     it greys out with a disabled button. */
  .tray-icon {
    width: 1.2em;
    height: 1.2em;
    margin-right: 0.3em;
    fill: currentColor;
    vertical-align: -0.25em;
  }
  /* .theme-options (#167, browser-local override -- see loadStoredTheme's
     own comment) is a radio group in the settings dialog. Deliberately not
     an .edit-field: that rule's bordered, padded input styling is meant for
     text inputs and would box each radio. Option text inherits the dialog's
     own colour, which the dark rules below set; a var(--primary-text-color)
     here stays dark on dark. */
  .theme-options {
    margin: 8px 0;
    padding: 0;
    border: 0;
  }
  .theme-options legend {
    padding: 0;
  }
  .theme-option {
    display: block;
    margin: 4px 0;
  }
  /* .choice-row (#173) is the highlight bar on every selectable row in a
     dialog: the theme radios, the Appliance picker and both Unmanaged Outlet
     tick-box lists. A light tint follows the mouse or keyboard focus and
     a strong one marks what is chosen; a disabled row (e.g. the one
     holding the current Appliance) stays plain. The checked and disabled
     rules sit last and out-rank :hover, so a hovered chosen row keeps its
     strong tint. Mixing towards transparent lets the row's own background
     show through in both themes. Group headings are not rows and get no
     class. */
  .choice-row {
    padding: 2px 6px;
    border-radius: 4px;
    cursor: pointer;
  }
  .choice-row:hover,
  .choice-row:focus-within {
    background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent);
  }
  .choice-row:has(input:checked) {
    background: color-mix(in srgb, var(--primary-color, #03a9f4) 30%, transparent);
  }
  .choice-row:has(input:disabled) {
    background: none;
    cursor: default;
  }
  /* min-height: 0 overrides flexbox's default min-height: auto on a flex
     child, which would otherwise let this grow to fit its content instead of
     respecting the flex parent's height -- the actual scroll container, so
     the header-bar above stays a plain, non-overlapping sibling rather than
     an overlay sharing its scrollbar. It does not scroll itself -- .panes
     below it does, so each of the three tables can scroll independently. */
  .scroll-region {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .panes {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    align-items: stretch;
    /* "safe" -- plain justify-content: center on a flex row that ends up
       wider than its container is a well-documented CSS trap: default
       ("unsafe") centering can push the *start*-side item's overflow past
       the container's start edge with nothing able to scroll back to it,
       so it silently vanishes while the end-side item stays fully visible
       -- exactly the asymmetric "Isolated Appliances disappears, Isolated
       Unmanaged Outlets stays visible" narrow-window bug this fixes. "safe"
       falls back to start-alignment once content overflows, guaranteeing
       everything stays reachable; centers normally whenever it fits. */
    justify-content: safe center;
    gap: 4px;
  }
  /* Every pane scrolls its own table. A pane sized to its table's
     fractional width (e.g. 653.3px) loses that fraction once a vertical
     scrollbar takes its ~15px, and the browser then shows a horizontal
     scrollbar with nothing to scroll -- caught live (#290) whenever the
     central table's bottom section was expanded. Reserving the vertical
     scrollbar's gutter up front keeps the width from depending on whether
     it shows; tried live against a 1px padding-inline-end, which did not
     help. Overlay scrollbars (Android) have no gutter, so this is a no-op
     there. */
  .pane {
    scrollbar-gutter: stable;
  }
  /* A fixed 280px basis, not sized off content (#331): a card band drops a
     collapsed section's cards from the DOM, so a content-sized pane would
     shrink and shift the row on every collapse. Cards fill the width, so a
     fixed basis leaves no slack. It can still shrink when the row doesn't
     fit. */
  .pane-side {
    flex: 0 1 280px;
    max-width: 280px;
    overflow-y: auto;
  }
  /* flex-grow: 0, not 1 -- a growing pane-main would consume all remaining
     row width, and the CO table (width: auto; margin: 0 auto, from the base
     .structured-table rule) would then center its own narrower content
     *inside* that oversized pane, leaving a visible gap to the side panes
     despite .panes' own small gap. Sized off its own content instead,
     matching .pane-side, so the group of three panes sits close together and
     .panes' justify-content: center above centers the group as a whole.
     min-width: 0 is still what lets this pane shrink below its table's
     natural width when the row doesn't fit -- without it a flex item refuses
     to go under its content size, so an over-wide CO table would widen the
     whole three-pane row and push a side pane off-screen instead of
     scrolling inside its own pane. */
  .pane-main {
    flex: 0 1 auto;
    min-width: 0;
    overflow: auto;
  }
  /* #290's medium tier: one pane at a time, chosen by the tab row
     below. Only the Smart Devices tab uses this; the Appliances and Unmanaged
     Outlets tabs render capped cards (.entity-cards).
     Replaces the old max-width: 900px rule that stacked all three
     panes -- that keyed on the viewport, and the tier has to change the
     DOM anyway (tabs, one table), so it lives in panel.ts's ResizeObserver
     state instead. min-width: 0 lets the pane shrink below its table's
     natural width and scroll that table inside itself, same as
     .pane-main above. */
  .pane-single {
    flex: 1 1 auto;
    min-width: 0;
    overflow: auto;
  }
  table {
    border-collapse: collapse;
    width: 100%;
  }
  th,
  td {
    text-align: left;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
  }
  th {
    padding: 4px 12px 4px 0;
  }
  td {
    vertical-align: top;
    padding: 8px 12px;
  }
  /* The pending-value cell marker (#190) -- a bare asterisk, deliberately
     not backtick-quoted in this comment since it sits inside a template
     literal. Just enough to be visible and discoverable (cursor: help hints
     at the tooltip carrying what Commit will do) -- the sibling .pending row
     class it sits alongside carries no styling of its own here at all; a
     tint/border treatment for a pending row or value is undecided. */
  .pending-marker {
    appearance: none;
    border: none;
    background: none;
    padding: 0;
    font: inherit;
    cursor: help;
    margin-right: 2px;
    /* WCAG 2.5.8 tap target, as a real box rather than a positioned
       ::before -- a positioned pseudo-element would paint over the
       neighbouring link button and take its taps (#312). */
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 24px;
    min-height: 24px;
  }
  /* The one shared tooltip popover (#312): position: fixed, rendered once
     outside .scroll-region so nothing clips it. Its colours, corners and
     shadow are the Hover box surface's, and its text the Hover styles'. */
  /* A manual popover (#546), in the top layer above any open dialog. inset,
     margin and border undo the UA [popover] style, which centres and frames
     it; the UA's :not(:popover-open) rule hides it. */
  .tooltip-popover {
    position: fixed;
    inset: auto;
    margin: 0;
    border: none;
    box-sizing: border-box;
    max-width: min(40ch, calc(100vw - 16px));
    max-height: calc(100vh - 16px);
    overflow: hidden;
    padding: 6px 10px;
    white-space: pre-wrap;
    pointer-events: none;
  }
  .tip-title + .tip-body {
    margin-top: 0.6em;
  }
  /* Hanging indent: the marker is a fixed-width column (--tip-marker is
     the longest marker in this body), so wrapped text and a group's
     continuation lines align under the item's text. */
  .tip-line {
    display: flex;
    gap: 0.5ch;
  }
  .tip-marker {
    flex: none;
    min-width: var(--tip-marker, 0);
  }
  .tip-text-cell {
    flex: 1 1 auto;
    min-width: 0;
    overflow-wrap: anywhere;
  }
  /* A blank line in a body keeps one line's height. */
  .tip-text-cell:empty::before {
    content: "\\a0";
  }
  /* The hover format (#556): one label column per hover, right-aligned, so
     the colons line up; a breakdown item hangs from the left edge. */
  .tip-icon,
  .tip-no-entry {
    width: 1.1em;
    height: 1.1em;
    vertical-align: -0.2em;
    margin-right: 0.5ch;
    fill: currentColor;
  }
  .tip-no-entry {
    fill: var(--tip-stop);
  }
  .tip-no-entry.end {
    margin-right: 0;
    margin-left: 0.5ch;
  }
  /* A blocked action is set apart from the title by a blank line. */
  .tip-action.blocked {
    margin-top: 0.6em;
  }
  .tip-attrs {
    display: grid;
    grid-template-columns: max-content minmax(0, 1fr);
    column-gap: 1ch;
    margin-top: 0.6em;
  }
  .tip-attr-label {
    grid-column: 1;
  }
  .tip-attr-value {
    grid-column: 2;
    overflow-wrap: anywhere;
  }
  .tip-attr-item {
    grid-column: 1 / -1;
    padding-left: 4ch;
    text-indent: -2ch;
    overflow-wrap: anywhere;
  }
  .new-badge {
    display: inline-block;
    margin-left: 6px;
    padding: 0 5px;
    border-radius: 8px;
    vertical-align: text-top;
    background: var(--primary-color, #03a9f4);
  }
  .attr-list {
    margin: 2px 0 0 0;
    padding-left: 16px;
  }
  .structured-table .attr-list {
    padding-left: 14px;
  }
  .link-btn {
    border: none;
    background: none;
    cursor: pointer;
    font: inherit;
    display: inline-flex;
    align-items: center;
    padding: 0 2px;
    vertical-align: middle;
    opacity: 0.15;
    transition: opacity 0.15s ease;
  }
  .link-btn:hover,
  .link-btn:focus-visible {
    opacity: 1;
  }
  /* Sized off em so it tracks whatever font-size is in effect on the
     button -- the base 0.85em on .link-btn above, or the prominent
     1.6rem below in the panel's vacant state -- the way emoji text
     would (#106). */
  .link-icon {
    width: 1em;
    height: 1em;
    fill: var(--ob-icon-colour, currentColor);
    vertical-align: middle;
  }
  .link-btn .link-icon {
    width: 0.85em;
    height: 0.85em;
  }
  /* Debug-only (#246) -- deliberately unlike .link-btn/.entity-link-primary
     (no border, solid fill on hover) so it reads as debug-only rather
     than an ordinary row control: a dashed error-colored outline. Small
     and icon-only at 75% opacity by default (visible without hovering,
     unlike .link-btn's 0.15-until-hover), expanding on hover/focus to
     full opacity plus its "Delete" label via .debug-delete-label below --
     live feedback was that hover-to-reveal-everything read as too easy to
     miss, but a permanently-expanded label read as too prominent for a
     debug-only control sitting in the middle of ordinary row content. */
  .debug-delete-btn {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    border: 1px dashed var(--error-color, #b00020);
    background: none;
    border-radius: 4px;
    cursor: pointer;
    padding: 0 3px;
    vertical-align: middle;
    margin-right: 4px;
    opacity: 0.75;
    transition:
      opacity 0.15s ease,
      background 0.15s ease,
      color 0.15s ease;
  }
  .debug-delete-btn:hover,
  .debug-delete-btn:focus-visible {
    opacity: 1;
    background: var(--error-color, #b00020);
  }
  .debug-delete-icon {
    width: 1em;
    height: 1em;
    fill: currentColor;
    vertical-align: middle;
    flex: none;
  }
  /* Collapsed to zero width by default (icon-only button); max-width is
     the animatable stand-in for width:auto, which transitions don't
     support. */
  .debug-delete-label {
    max-width: 0;
    overflow: hidden;
    white-space: nowrap;
    opacity: 0;
    transition:
      max-width 0.15s ease,
      opacity 0.15s ease;
  }
  .debug-delete-btn:hover .debug-delete-label,
  .debug-delete-btn:focus-visible .debug-delete-label {
    max-width: 50px;
    opacity: 1;
  }
  /* Unlike .link-btn, a create button is always visible rather
     than dim-until-hover -- there's no existing content nearby to declutter
     against (it sits in an otherwise-plain <th>), so it reads as a small
     pill-shaped button rather than an icon affordance. Sticky <th>
     headers -- .th-appliance/.th-uo already center their text
     (see below); the button rides inline beside it rather than needing
     its own layout rule. */
  .structured-table thead .create-btn {
    margin-left: 6px;
    padding: 2px 9px;
    font: inherit;
    vertical-align: middle;
    color: var(--ob-btn-plain-text);
    background: none;
    border: 1px solid currentColor;
    border-radius: 10px;
    cursor: pointer;
    transition: background-color 0.15s ease-out;
  }
  /* Outlined, like the session toolbar: a tint on hover, not a fill. */
  .structured-table thead .create-btn:focus-visible {
    background: color-mix(in srgb, currentColor 14%, transparent);
  }
  @media (hover: hover) {
    .structured-table thead .create-btn:hover {
      background: color-mix(in srgb, currentColor 14%, transparent);
    }
  }
  .link-btn.linked {
    --ob-icon-colour: var(--ob-icon-linked);
  }
  /* Both states prominent/always visible in the central table (the
     .structured-table ancestor guard keeps other .link-btn uses out of it).
     The linked ("unplug") state is a red, unmistakably-"unplug"-shaped glyph
     (.link-icon, fill: currentColor, picking up .link-btn.linked's color:
     var(--error-color) below) rather than a generic ⏏️ emoji (#106), so
     there is no reason to keep it small or dim. */
  .structured-table .link-btn,
  .entity-cards .link-btn {
    opacity: 1;
  }
  .structured-table .link-btn .link-icon,
  .entity-cards .link-btn .link-icon {
    /* rem, not em -- em on font-size resolves against the *parent's*
       computed size (that part of the cascade is correct), but
       devtools showed that parent resolving to only ~9.8px here
       (1.8em -> 17.68px), some local cascade quirk rather than the
       page's real body text size. A bare fixed px would dodge that
       but stop responding to a user's browser/OS accessibility
       text-size setting -- rem keeps that responsiveness (it scales
       with the root font-size, which *does* track those settings)
       while sidestepping whatever's happening in this local chain. */
    width: 1.6rem;
    height: 1.6rem;
  }
  /* The link button is an inline SVG (.link-icon, fill: currentColor)
     rather than an emoji glyph, which browsers always render in full color
     regardless of the CSS color property, so this color rule applies. */
  .structured-table .link-btn:not(.linked),
  .entity-cards .link-btn:not(.linked) {
    --ob-icon-colour: var(--ob-icon-plug);
  }
  /* Nothing available on the other end to plug into right now -- the button stays real-disabled (see the
     ?disabled= binding in _renderLinkButton), so this is a secondary
     visual confirmation of that, not the only signal. */
  .structured-table .link-btn:not(.linked).unavailable,
  .entity-cards .link-btn:not(.linked).unavailable {
    --ob-icon-colour: var(--ob-icon-unavailable);
  }
  /* The box's look (colour, corners, shadow, border, the dark frosting and
     the backdrop) is the "modal-dialog-box" surface, named in each dialog's
     class (surface-styles.ts); this is only its size and spacing. */
  dialog {
    padding: 16px 20px;
    min-width: 360px;
    max-width: 640px;
    min-height: 320px;
    max-height: calc(100vh - 6em);
  }
  /* dialog[open] rather than plain dialog for display:flex -- an
     author-origin rule on the bare element beats the UA stylesheet's
     dialog:not([open]) { display: none } regardless of specificity,
     so plain "display: flex" here kept a closed dialog permanently
     laid out on the page instead of hidden. */
  dialog[open] {
    display: flex;
    flex-direction: column;
  }
  /* Flex item, not the scroll container itself -- .dialog-body scrolls
     so .dialog-actions (a sibling flex item) stays a fixed size and
     gets pinned to the box's bottom edge by flex-grow on the body,
     both when content overflows and when it's shorter than min-height. */
  .dialog-body {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
  }
  .dialog-title {
    margin: 0 0 8px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
  }
  /* The build in a dialog title in debug mode (#684). */
  .build-stamp {
    margin-left: 0.75em;
  }
  /* A confirm dialog's consequence listing (#300) -- what an irreversible
     action would act on, one bullet per staged group. No explicit color:
     inherits from the dialog's own text color (set per mode by the
     "modal-dialog-box" surface), avoiding a second light/dark pair to keep
     in sync. list-style: none -- the manual "N. " prefix
     each line already carries (panel.ts's _renderConsequenceLines) is the
     only marker needed; a bullet dot would double up with it. white-space:
     pre-wrap (inherited by the <li> children) makes a multi-entry group's
     embedded "\n" and four-space indent for its continuation lines render as
     a real line break and visible indent here, the same way the shared
     tooltip popover renders the same string via its own pre-wrap. */
  .consequence-list {
    margin: 0 0 8px 0;
    padding-left: 20px;
    list-style: none;
    white-space: pre-wrap;
  }
  /* Always the confirm dialog's last line (#300) -- "cannot be undone" is
     never concatenated into the question sentence, so it reads as a
     distinct, unmissable warning regardless of how long the listing above
     it gets. A fixed flex item (flex: 0 0 auto) and a sibling of
     .dialog-body rather than a child of it -- .dialog-body is the
     scrolling region (long listings), so a warning living inside it could
     scroll out of view together with the buttons. As a sibling it stays
     pinned directly above .dialog-actions' separator line, visible
     whenever the buttons are. */
  .irreversible-warning {
    flex: 0 0 auto;
    margin: 8px 0 0 0;
    text-align: center;
  }
  /* Commit's own last line (#301) -- same fixed-sibling
     positioning as .irreversible-warning above (see its own comment), but
     amber rather than red: committing writes real, un-staged changes to
     the live system, not the data loss Flush/Delete's red line warns
     about, so a different colour keeps the two severities visually
     distinct rather than reusing red for something that isn't the same
     kind of destructive. */
  .write-warning {
    flex: 0 0 auto;
    margin: 8px 0 0 0;
    text-align: center;
  }
  .plugged-into {
    margin: 0 0 8px 0;
  }
  .entity-id {
    margin: 12px 0 0 0;
    padding: 0;
    list-style: none;
  }
  .entity-id li {
    margin: 2px 0;
  }
  .entity-id .id-row {
    margin-top: 22px;
    padding-top: 6px;
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }
  /* The Smart Device's link to its Home Assistant page (#522) sits last in
     the details list, at the right edge, but keeps the dialog's own font:
     its class is the Dialog field note's, not the list's metadata size. */
  .entity-id .ha-device-link {
    text-align: right;
  }
  /* An Appliance's "Home Assistant items" kebab (#599): straight after the name
     in its edit dialog's title. A plain button that reads as the dots alone,
     dropped so the dots sit on the text rather than above it. */
  .ha-items-wrap {
    display: inline-block;
    margin-left: 0.2em;
    vertical-align: -0.25em;
  }
  .ha-items-btn {
    display: inline-flex;
    align-items: center;
    padding: 0;
    border: 0;
    background: none;
    font: inherit;
    cursor: pointer;
  }
  .ha-items-btn:disabled {
    cursor: default;
  }
  .ha-items-icon {
    width: 1em;
    height: 1em;
    fill: currentColor;
  }
  /* The Home Assistant items dialog: its title and prompt stay put and only
     the list scrolls. It is as tall as its list, where other dialogs keep a
     minimum height. */
  .ha-items-dialog {
    min-height: 0;
  }
  .ha-items-head {
    flex: none;
  }
  /* The padding holds the rows' clickable room, which spills past their
     text, so a list that fits has nothing to scroll or bounce. */
  .ha-items-scroll {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 4px;
  }
  /* The list and each group stack their rows with a gap, and a row stretches
     across, so the whole line is what is hovered and pressed. */
  .ha-items-scroll,
  .ha-items-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .ha-items-prompt {
    margin: 0 0 4px;
  }
  /* One item: its name, then the logo, the whole row a link. Under a domain
     heading the items are indented; the clickable text's own margin is
     already taken, so the indent is added to it. */
  .ha-item {
    display: flex;
    align-items: center;
  }
  .ha-items-group-heading {
    margin: 8px 0 0;
  }
  .ha-items-group .ha-item {
    margin-left: calc(1.5em - 3px);
  }
  /* The logo is drawn in the colour a link has, as the logo links elsewhere
     are, which a button's inherited colour would lose. */
  .ha-item .ha-icon {
    margin-left: 0.4em;
    fill: LinkText;
  }
  /* The Home Assistant logo after the link's text, and alone as a link on a
     line naming a Smart Device (#522): it takes the link's colour, so all
     match. */
  .ha-icon {
    width: 1.1em;
    height: 1.1em;
    margin-left: 0.3em;
    vertical-align: -0.2em;
    fill: currentColor;
  }
  /* A logo-only link sits right after its line's text, or, on the Smart
     Device edit dialog's title, at the dialog's right edge (#522). */
  .ha-device-icon-link.edge {
    float: right;
  }
  /* The gap before an inline logo is a real space, widened: it collapses
     where the line wraps, as a margin would not. */
  .ha-gap {
    word-spacing: 1.55em;
  }
  .ha-device-icon-link .ha-icon {
    margin-left: 0;
  }
  /* The device dialog's Sockets list (#449): one line per socket, its Edit
     button pushed to the right edge. */
  .socket-list {
    margin: 12px 0 0 0;
  }
  .socket-list p {
    margin: 0 0 4px 0;
  }
  .socket-list ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .socket-list-line {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
  }
  /* The meter's space is held on an unmetered socket too, so every
     line's label starts in the same column. */
  .socket-list-meter {
    flex: none;
    width: 1em;
    display: inline-flex;
  }
  .socket-list-occupant {
    flex: 1 1 auto;
  }
  .edit-field {
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin: 8px 0;
  }
  /* Room/CO filter dropdowns (#99) -- one per row, the select to the right
     of its label, each an .edit-field internally so they reuse its styling
     below unchanged; only their shared layout is new. */
  .link-filters {
    display: grid;
    grid-template-columns: max-content minmax(0, 1fr);
    align-items: center;
    gap: 6px 8px;
  }
  .link-filters .edit-field {
    display: contents;
  }
  .edit-field input,
  .edit-field select {
    font: inherit;
    padding: 6px 8px;
    border: 1px solid var(--divider-color, #e0e0e0);
    border-radius: 4px;
    background: var(--card-background-color, #fff);
    color: inherit;
  }
  .area-hint {
    margin: 0;
  }
  .dialog-actions {
    flex: 0 0 auto;
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 16px;
    padding-top: 8px;
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }
  /* As HA's dialogs: Cancel and Close are plain (coloured text, no
     outline), the last button is the filled main action. */
  .dialog-actions button {
    font: inherit;
    padding: 6px 14px;
    border: 1px solid transparent;
    border-radius: 4px;
    background: none;
    color: var(--ob-btn-plain-text);
    cursor: pointer;
    transition: background-color 0.15s ease-out;
  }
  .dialog-actions button:last-of-type:not(:disabled) {
    background: var(--ob-btn-main);
    color: var(--ob-btn-on-fill);
  }
  /* Same specificity as button:last-of-type above -- wins only because
     it is declared after it, since the destructive action (Unplug) is
     sometimes itself the last button in the row (e.g. the multi
     dialog, or an occupied CO Socket's unplug-only confirm). */
  .dialog-actions button.danger:not(:disabled) {
    background: var(--ob-btn-danger);
    color: var(--ob-btn-on-fill);
  }
  /* Same reasoning as button.danger above -- Commit's own confirm dialog
     (#301 follow-up) needs green, not button:last-of-type's default blue.
     The last-button, danger and go colours are for enabled buttons only:
     a disabled one is a grey block, as in HA. */
  .dialog-actions button.go:not(:disabled) {
    background: var(--ob-btn-go);
    color: var(--ob-btn-on-fill);
  }
  .dialog-actions button:disabled {
    background: var(--ob-btn-disabled-fill);
    color: var(--ob-btn-disabled-text);
    cursor: default;
  }
  /* The control a dialog opens on (its \`autofocus\` one) always shows its focus
     ring. The browser draws a ring for keyboard focus only, and a dialog the
     mouse opened would show none, so the ring looked different each time. */
  dialog [autofocus]:focus {
    outline: 2px solid var(--primary-color, #03a9f4);
    outline-offset: 1px;
  }
  /* Hover darkens a filled button and tints a plain one, only where there
     is a pointer, so a tap does not leave a button in its hover colour. */
  @media (hover: hover) {
    .dialog-actions button:not(:disabled):hover {
      background: var(--ob-btn-plain-hover);
    }
    .dialog-actions button:last-of-type:not(:disabled):hover {
      background: var(--ob-btn-main-hover);
    }
    .dialog-actions button.danger:not(:disabled):hover {
      background: var(--ob-btn-danger-hover);
    }
    .dialog-actions button.go:not(:disabled):hover {
      background: var(--ob-btn-go-hover);
    }
    .menu-btn:hover,
    .main-filter-open:hover,
    .main-filter-close:hover {
      background: var(--ob-btn-icon-hover);
    }
    .plain-btn:not(:disabled):hover {
      background: var(--ob-btn-plain-hover);
    }
  }
  /* A button inside a dialog's body (Tick all, Untick all, a socket's
     Edit): plain, like Cancel. */
  .plain-btn {
    font: inherit;
    padding: 4px 10px;
    border: 1px solid transparent;
    border-radius: 4px;
    background: none;
    color: var(--ob-btn-plain-text);
    cursor: pointer;
    transition: background-color 0.15s ease-out;
  }
  .plain-btn:disabled {
    color: var(--ob-btn-disabled-quiet);
    cursor: default;
  }
  .link-candidates {
    list-style: none;
    margin: 8px 0;
    padding: 0;
    max-height: 340px;
    overflow-y: auto;
  }
  .no-candidates {
    margin: 0;
  }
  .link-candidates li {
    margin: 4px 0;
  }
  .link-candidates label {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  /* #424: a CO's picker draws its Unmanaged Outlets and its other sockets as two
     lists, an empty one with its heading and a line saying so. Stacked by
     default; side by side, in a wider dialog, when the panel is wide enough.
     Each list scrolls on its own. */
  .link-lists {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px 20px;
  }
  .link-lists.side-by-side {
    grid-template-columns: 1fr 1fr;
    align-items: start;
  }
  dialog.link-dialog.side-by-side {
    width: min(900px, calc(100vw - 6em));
    max-width: none;
  }
  .link-list-title {
    margin: 4px 0 0 0;
  }
  .candidate-group {
    margin: 4px 0;
  }
  .candidate-group-label {
    margin-bottom: 2px;
  }
  .candidate-group-items {
    list-style: none;
    margin: 0;
    padding-left: 16px;
  }
  /* The "Appliances from Socket names" dialog (#394): wider than the other
     dialogs, its .dialog-body scrolling the table. The Tick all / Untick all
     row and the count sit above the table. The "Wall Sockets for Smart
     Devices" dialog shares this width, the toolbar with its own Tick all /
     Untick all, and the table and field classes below. */
  .from-names-dialog,
  .wall-batch-dialog {
    width: fit-content;
    max-width: calc(100vw - 4em);
  }
  /* Only the table scrolls: the title and the counts stay in view above it,
     with the sticky column headings pinned to the top of the scrolling
     region. If .dialog-body scrolled instead, the title and counts would
     scroll away while the headings stayed. */
  .from-names-dialog .dialog-body,
  .wall-batch-dialog .dialog-body {
    display: flex;
    flex-direction: column;
    overflow-y: hidden;
  }
  .from-names-scroll {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
  }
  /* The Export dialog (#532): the format radios sit in a plain fieldset. */
  .export-formats {
    border: none;
    margin: 0 0 8px 0;
    padding: 0;
  }
  .export-formats legend {
    padding: 0;
    margin-bottom: 4px;
  }
  .export-notice {
    margin: 8px 0 0 0;
  }
  .from-names-toolbar {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0 0 8px 0;
  }
  .from-names-counts {
    margin-left: auto;
  }
  .from-names-table {
    border-collapse: collapse;
  }
  /* The Appliance name column: as wide as a name needs, not as wide as the
     dialog; its heading, slug and notes wrap inside it. */
  .from-names-col-name {
    width: 40ch;
    max-width: 40ch;
  }
  /* A row's note sits on its own line beneath it, across the name and HA
     name columns; the row above drops its bottom rule so the two read as
     one. */
  .from-names-has-note td:not(.from-names-integration) {
    border-bottom: none;
  }
  .from-names-note-row .from-names-note {
    margin: 0;
  }
  .from-names-table th,
  .from-names-table td {
    text-align: left;
    vertical-align: top;
    padding: 4px 8px;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
  }
  .from-names-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #fff;
    border-bottom: 2px solid var(--divider-color, #e0e0e0);
  }
  .from-names-integration {
    white-space: nowrap;
  }
  .from-names-name {
    width: 100%;
    box-sizing: border-box;
    min-width: 12ch;
  }
  /* Read-only: plain text. Editable (its row is ticked): a boxed field in
     the accent colour, so the change is unmistakable. */
  .from-names-name[readonly] {
    border: 1px solid transparent;
    background: transparent;
    color: inherit;
  }
  .from-names-name:not([readonly]) {
    border: 2px solid var(--primary-color, #03a9f4);
    border-radius: 4px;
    background: #fff;
    color: inherit;
    padding: 3px 6px;
  }
  /* A ticked row's radio group (#395): one option per line, in smaller text,
     each option's label wrapping inside its own line. */
  .wall-batch-options {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  .wall-batch-options .from-names-name {
    align-self: stretch;
  }
  /* The filter bar every choosing dialog has (#485): any further controls
     the dialog adds come first, and the text input sits below them. */
  .dialog-filter {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }
  .dialog-filter-input {
    min-width: 16ch;
    box-sizing: border-box;
    border: 1px solid var(--divider-color, #9e9e9e);
    border-radius: 4px;
    background: #fff;
    color: inherit;
    padding: 3px 6px;
  }
  .from-names-name:not([readonly]):focus {
    outline: 2px solid var(--primary-color, #03a9f4);
    outline-offset: 1px;
  }
  /* The slug of the name, the part of the entity_id it supplies: read-only, and
     monospace so it can be read character by character and copied. */
  .from-names-slug {
    margin: 2px 0 0 0;
    overflow-wrap: anywhere;
    user-select: text;
  }
  .from-names-note {
    margin: 2px 0 0 0;
  }
  .from-names-error {
    display: flex;
    align-items: flex-start;
    gap: 4px;
  }
  .from-names-error-icon {
    flex: 0 0 auto;
    width: 1.2em;
    height: 1.2em;
    fill: currentColor;
  }
  /* A ticked row that keeps Apply disabled -- also marked by its note. */
  .from-names-blocked td:not(.from-names-integration) {
    background: rgba(176, 0, 32, 0.08);
  }
  .candidate-note,
  .candidate-context {
    margin: 0 0 0 24px;
  }
  .link-row-error {
    margin: 2px 0 0 24px;
  }
  .structured-table {
    width: auto;
    margin: 0 auto;
  }
  .structured-table thead th {
    position: sticky;
    top: 0;
    z-index: 5;
    background: #fff;
    border-bottom: 2px solid var(--divider-color, #e0e0e0);
  }
  /* The plug-vs-socket-cluster split sits in the two dedicated
     .th-connection headers between the flanking entities (below), one
     identical plug+unplug pair each (#109). The regional socket icon stays
     local to the entity it actually describes -- pinned to the extreme left
     edge of the Smart device/Unmanaged Outlet headers that own it, not shared
     into the Connection columns. */
  .structured-table thead .th-appliance {
    text-align: center;
    vertical-align: middle;
    min-width: 14ch;
  }
  /* #167: column-width floors, paired with the matching
     .appl-cell/.co-cell/.uo-cell/.connection-cell floors below --
     placeholders, to be checked against real seed data (longest appliance
     name, longest CO alias/MAC+location line, longest uo name).
     Deliberately scoped to the columns/cells themselves, not
     .pane-side/.pane-main (see the comments on those two rules) -- a fixed
     or min-width wrapper there causes a visible gap around narrower content,
     and can push a side pane off-screen. */
  .structured-table thead .th-co {
    min-width: 22ch;
  }
  .structured-table thead .th-uo {
    min-width: 16ch;
  }
  .structured-table thead .th-connection {
    min-width: 3em;
  }
  /* #167: the co-table's column-linking tint -- painted per cell, since the
     table itself carries no background. Cards carry no tint. */
  .co-table .th-appliance,
  .co-table .appl-cell {
    background-color: var(--column-tint-appliance);
  }
  .co-table .th-uo,
  .co-table .uo-cell {
    background-color: var(--column-tint-uo);
  }
  /* #140: each content header stacks its label (or icon+label .th-row) over
     the column's total, centered. display:flex must live on this wrapper,
     never on the <th> itself -- see the .th-row comment just below for why.
     min-height (not on the <th> -- box-sizing/min-height set directly on a
     sticky <th> render with zero effect on this table's auto layout) lives
     here instead, since the <th>'s own rendered height in auto table layout
     is driven by its content's natural size -- growing the wrapper genuinely
     grows the cell. justify-content: center re-centers the two stacked lines
     within that taller box (align-items above only centers the column's
     *cross* axis, i.e. horizontally, for a flex-direction: column
     container). */
  .structured-table thead .th-stack {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    min-height: var(--structured-header-min-height);
    box-sizing: border-box;
  }
  /* display:flex must live on this inner wrapper, never on the <th>
     itself -- a <th>/<td> with its own display overridden away from
     table-cell stops sizing to the table's real column width in some
     browsers (its border-bottom then only wraps the flex content's
     shrink-to-fit size instead of the full column), which is exactly
     the "broken-looking" header border a live check caught. */
  .structured-table thead .th-row {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  /* min-height only when .th-row is the <th>'s OWN direct wrapper (the
     isolated tables' New-button row, and .th-connection's icon row) --
     scoped with a direct-child selector rather than the plain
     .structured-table thead .th-row rule above, so a floor applied here
     can't stack on top of some other nested .th-row a future header adds
     inside .th-stack and overshoot every other column's height.
     th-co/th-uo don't nest a .th-row inside .th-stack today (each
     is a single <span> directly in .th-stack), but the direct-child scope
     stays as a guard against reintroducing that stacking bug later. */
  .structured-table thead th > .th-row {
    min-height: var(--structured-header-min-height);
    box-sizing: border-box;
  }
  .structured-table thead .th-content {
    flex: 1 1 auto;
    text-align: center;
  }
  /* Both icons (plug + unplug) render together, identically, in both
     Connection headers -- see connectionHeaderIcons in
     panel.ts. Equal content in both columns keeps their
     auto-computed widths equal too. */
  .structured-table thead .th-connection .th-row {
    justify-content: center;
    gap: 3px;
  }
  /* Muted blue-grey/red-grey rather than flat neutral grey, hinting at
     the same plug/unplug color semantics the row-level .link-btn icons
     use (var(--primary-color)/var(--error-color)), without the header
     icons competing for attention the way the full-strength row icons do
     color-mix() picks up whatever HA theme is
     active rather than a hardcoded pair; the 55% blend is a starting
     point to eyeball live, not a measured constant. */
  .structured-table thead .th-connection .th-icon.plug {
    --ob-icon-colour: color-mix(in srgb, var(--ob-icon-plug) 55%, var(--ob-icon-quiet));
  }
  .structured-table thead .th-connection .th-icon.unplug {
    --ob-icon-colour: color-mix(in srgb, var(--ob-icon-linked) 55%, var(--ob-icon-quiet));
  }
  .th-icon {
    width: 1.1em;
    height: 1.1em;
    fill: var(--ob-icon-colour, currentColor);
    vertical-align: middle;
  }
  .structured-table td,
  .structured-table th {
    border-bottom: none;
  }
  /* #109: narrow, icon/button-only columns -- tighter padding than the
     content columns either side of them. */
  .structured-table td.connection-cell {
    text-align: center;
    vertical-align: middle;
    padding: 8px 4px;
    min-width: 3em;
  }
  .structured-table td.uo-cell {
    vertical-align: middle;
    min-width: 16ch;
  }
  /* #535: every cell of the central table chooses its vertical alignment, so
     a socket's own column sits level with the Appliance beside it. */
  .structured-table td.socket-cell {
    vertical-align: middle;
  }
  .structured-table .row-shade {
    background: rgba(127, 127, 127, 0.06);
  }
  .structured-table .appl-cell {
    text-align: right;
    vertical-align: middle;
    min-width: 14ch;
  }
  /* #308: left-justified -- not docked rightward toward the co-connection
     button the way .appl-cell still docks toward its own connection button.
     Since text-align is the same direction the
     manufacturer:model/MAC-or-alias lines already read in, no inline-block
     wrapper is needed to keep them reading left-to-right independently of
     the td's own alignment. */
  .structured-table .co-cell {
    text-align: left;
    min-width: 22ch;
    /* This cell is often rowspan'd across several socket rows (one
       device, several sockets) -- vertically centering it within that
       span reads better than pinning it to the top of the tallest
       socket-row stack, and costs nothing when it isn't spanned. */
    vertical-align: middle;
  }
  /* #510: the table's device box -- the identity beside the "plugged into"
     text. The grid sits on this inner div, never the td; the gap is the
     invisible separator. */
  .co-box {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    column-gap: 12px;
  }
  .co-box-model {
    margin-top: 2px;
  }
  .co-box-delete {
    margin-bottom: 2px;
  }
  /* Read top to bottom, toward the PCO's plug button's column. The
     inline-size cap (vertical here) wraps a long host name into a second
     column instead of making a one-socket box very tall. */
  .co-box-plugged {
    writing-mode: vertical-rl;
    max-inline-size: 12em;
    align-self: center;
  }
  .co-alias {
    margin-top: 2px;
  }
  .card-model {
    margin-left: 4px;
  }
  /* A name that opens something (an entity's own name, or a name in a
     dialog) is the "clickable text" look (#156), named in the button's class
     (control-styles.ts). A name that is held is hover-only and is no button. */
  .meter-icon {
    width: 1em;
    height: 1em;
    fill: currentColor;
    vertical-align: middle;
  }
  /* #308: a socket row's icon/appliance/connection cells are short by
     nature -- tighter than the default td padding keeps the box "as
     short as sensible". Excludes .co-cell: that's the rowspan'd device-
     identity cell, which sits beside these rows but isn't one of them,
     and needs its normal two-line padding regardless of how many socket
     rows it spans. Likewise .uo-cell and .co-connection, which sit in
     the first socket row's <tr> but are rowspan'd across several rows. */
  .structured-table
    tr.socket-row
    > td:not(.co-cell):not(.uo-cell):not(.co-connection) {
    padding-top: 4px;
    padding-bottom: 4px;
  }
  /* Groups one CO's own Smart device content -- its icon column (one cell
     per socket row) plus its identity cell (.co-cell, rowspan'd beside
     them, or the lone cell when there are no sockets) -- into a single
     visual box, distinguishing it from sibling COs sharing the same Unmanaged
     Outlet group. No line divides the icon column from .co-cell: the icon
     cell only gets the box's own LEFT edge (.co-box-left), .co-cell only
     gets the box's own RIGHT edge (.co-box-right); neither declares the
     shared inner edge, so nothing is there to collapse into a visible line.
     The 0-socket case has no separate icon cell, so its lone identity cell
     takes both classes. Top only on each CO's first row, bottom only on its
     last -- border-collapse: collapse (set on the table) merges the shared
     edges between adjacent cells in the set into one continuous line. */
  .structured-table .co-box-left {
    border-left: 1px solid var(--divider-color, #e0e0e0);
  }
  .structured-table .co-box-right {
    border-right: 1px solid var(--divider-color, #e0e0e0);
  }
  .structured-table .co-box-top {
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }
  .structured-table .co-box-bottom {
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
  }
  /* Tethers a Connection column's button to the content it belongs to
     (#109 follow-up) without widening a box or cell to swallow this
     whole narrow column -- a short stub in the same colour as the box
     border, reading as the neighbouring content reaching out to "its"
     button rather than the button looking orphaned in its own column.
     Each of these cells only ever has one leader, so the simple fix is
     docking the *whole cell's* content to the edge that leader needs to
     touch (padding zeroed on that side too) -- centering the group, as
     plain text-align:center would, leaves a gap between the leader and
     the edge it's meant to reach. */
  .structured-table td.co-connection {
    text-align: left;
    white-space: nowrap;
    padding-left: 0;
  }
  .structured-table td.socket-connection {
    text-align: right;
    white-space: nowrap;
    padding-right: 0;
  }
  .structured-table .connection-leader {
    display: inline-block;
    width: 16px;
    height: 1px;
    vertical-align: middle;
    background: var(--divider-color, #e0e0e0);
  }
  .structured-table .connection-leader.before {
    margin-right: 2px;
  }
  .structured-table .connection-leader.after {
    margin-left: 2px;
  }
  /* #424: a copy of a host, repeated above a CO in a lower band so a chain
     stays adjacent. Faded, italic, with a dashed outline in place of the live
     rows' solid box: it reads as context, and nothing
     in it is interactive (its cells are inert). The Unmanaged Outlet cell on
     its first row is left alone, since that cell is live. */
  .structured-table tr.copy-row > td:not(.uo-cell) {
    opacity: 0.55;
  }
  /* The dashes are painted as backgrounds, not dashed borders, so they draw
     the same in every browser: a dashed border in a collapsed-border table
     is painted per cell by each engine in its own way. Each edge class
     contributes one layer; the borders themselves are off, so the live row's
     solid top border wins where a copy meets it. */
  .structured-table tr.copy-row {
    --dash-v: repeating-linear-gradient(
      to bottom,
      var(--divider-color, #e0e0e0) 0 4px,
      transparent 4px 8px
    );
    --dash-h: repeating-linear-gradient(
      to right,
      var(--divider-color, #e0e0e0) 0 4px,
      transparent 4px 8px
    );
  }
  .structured-table tr.copy-row .co-box-left,
  .structured-table tr.copy-row .co-box-right,
  .structured-table tr.copy-row .co-box-top,
  .structured-table tr.copy-row .co-box-bottom {
    border: none;
    background-repeat: no-repeat;
    background-size:
      1px 100%,
      1px 100%,
      100% 1px,
      100% 1px;
    background-position:
      left top,
      right top,
      left top,
      left bottom;
    background-image:
      var(--dash-left, none), var(--dash-right, none), var(--dash-top, none),
      var(--dash-bottom, none);
  }
  .structured-table tr.copy-row .co-box-left {
    --dash-left: var(--dash-v);
  }
  .structured-table tr.copy-row .co-box-right {
    --dash-right: var(--dash-v);
  }
  .structured-table tr.copy-row .co-box-top {
    --dash-top: var(--dash-h);
  }
  .structured-table tr.copy-row .co-box-bottom {
    --dash-bottom: var(--dash-h);
  }
  /* #424: the power source at the top of a chained CO's card, beneath the host
     it hangs from: small, italic and grey, so it reads as background. */
  .power-source {
    display: block;
  }
  .hosting-mark {
    margin-right: 4px;
  }
  /* #424: an Appliance plugged straight into an Unmanaged Outlet -- a straight
     line across the Smart devices & Sockets column, between the Appliance's
     connection button and the outlet's own cell. */
  .structured-table tr.direct-row > td:not(.uo-cell) {
    padding-top: 4px;
    padding-bottom: 4px;
  }
  .structured-table td.direct-line-cell {
    padding-left: 0;
    padding-right: 0;
    vertical-align: middle;
  }
  .structured-table .direct-line {
    height: 1px;
    background: var(--divider-color, #e0e0e0);
  }
  .structured-table tr.section-header td {
    text-align: center;
    background: var(--secondary-background-color, rgba(127, 127, 127, 0.08));
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
  }
  /* #308: flex + width:100% + its own justify-content:center, not
     inline-flex relying on the td's inherited text-align:center -- a
     shrink-to-fit button leaves dead space on either side of it within the
     td, and that dead space would carry a DIFFERENT title (the section's
     counts) than hovering the button itself (the collapse/expand
     instruction) -- undiscoverable, since the visible label was never the
     thing showing the counts. Filling the whole cell with one element makes
     the hoverable area and the clickable area the same area, carrying one
     merged title (see
     _renderSectionCollapseToggle/_renderCardBandGroupToggle). The label
     still lives inside the button, widening the click target to cover it,
     not just the chevron icon. */
  .section-collapse-btn {
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    display: flex;
    width: 100%;
    justify-content: center;
    align-items: center;
    gap: 6px;
  }
  /* Disabled while the main filter has text (#529): the label stays readable,
     only the chevron dims. */
  .section-collapse-btn:disabled {
    cursor: default;
  }
  .section-collapse-btn:disabled .collapse-icon {
    opacity: 0.4;
  }
  /* Toggle plus its separate "i" button (#312): the ::before spacer is as
     wide as the "i", so the toggle's label stays centred in the header
     cell. Both the "i" and the spacer are dropped where the pointer can
     hover -- the toggle's own tooltip already shows the counts there. */
  .section-toggle-row {
    display: flex;
    align-items: center;
    width: 100%;
  }
  .section-toggle-row::before {
    content: "";
    flex: none;
    width: 24px;
  }
  .section-toggle-row .section-collapse-btn {
    flex: 1 1 auto;
    width: auto;
  }
  /* A real 24x24 box (WCAG 2.5.8) with a small, raised, italic serif
     glyph, matching the headings' superscript cue. */
  .info-btn {
    flex: none;
    appearance: none;
    border: none;
    background: none;
    padding: 0;
    min-width: 24px;
    min-height: 24px;
    display: inline-flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 3px;
    color: inherit;
    opacity: 0.6;
    cursor: help;
  }
  .info-btn:hover,
  .info-btn:focus-visible {
    opacity: 1;
  }
  @media (hover: hover) and (pointer: fine) {
    .info-btn,
    .section-toggle-row::before {
      display: none;
    }
  }
  .collapse-icon {
    width: 1em;
    height: 1em;
    fill: currentColor;
    vertical-align: middle;
  }
  /* Header menu button (#403) -- reuses .section-collapse-btn's borderless,
     color: inherit, inline-flex base, but icon-only: no label span sits next
     to a compact glyph in the header bar the way the collapse toggles' text
     labels do inline in a table row. The 24px box keeps it a real touch
     target (WCAG 2.5.8). */
  /* The filter icon beside it (#529) looks the same, under its own class so
     a query for the menu button cannot find it. */
  .menu-btn,
  .main-filter-open {
    border: none;
    background: none;
    padding: 0;
    min-width: 36px;
    min-height: 36px;
    border-radius: 50%;
    transition: background-color 0.15s ease-out;
    cursor: pointer;
    color: inherit;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .menu-icon {
    width: 1.4em;
    height: 1.4em;
    fill: currentColor;
    vertical-align: middle;
  }
  /* The menu itself: a plain positioned box under the button, right-aligned,
     not a <dialog>, so it is not modal and its tooltip stays visible (#312).
     z-index sits above the sticky table headers (5) and, with the
     tooltip popover (20), above everything else in the panel. Surface and
     text colours are the dialogs' own, with their dark overrides below. */
  .menu-wrap,
  .main-filter-wrap {
    position: relative;
  }
  .menu-list {
    position: absolute;
    top: 100%;
    right: 0;
    z-index: 20;
    box-sizing: border-box;
    min-width: 260px;
    max-width: min(360px, calc(100vw - 16px));
    margin-top: 4px;
    padding: 6px;
    border-radius: 8px;
    background: #fff;
    color: inherit;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  }
  .menu-list[hidden] {
    display: none;
  }
  /* A heading is a label, never a button. */
  .menu-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    padding: 6px 8px 2px;
  }
  .menu-entry {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 6px 8px;
    border: none;
    border-radius: 4px;
    background: none;
    font: inherit;
    color: inherit;
    text-align: left;
    cursor: pointer;
  }
  .menu-entry.indented {
    padding-left: 24px;
  }
  /* The same tint as .choice-row (#173): light on hover or keyboard focus. */
  .menu-entry:hover,
  .menu-entry:focus-visible {
    background: color-mix(in srgb, var(--primary-color, #03a9f4) 12%, transparent);
  }
  .menu-entry-icon {
    flex: none;
    width: 1.2em;
    height: 1.2em;
    fill: currentColor;
  }
  .menu-separator {
    margin: 6px 0;
    border: none;
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }
  /* #140: nothing else signals that a cell carries a hover tooltip at all.
     Applied to the three column-header labels, whose titles are counts --
     not a repo-wide sweep, other titles (e.g. edit-pencil buttons) are
     already self-evident from their icon. cursor: help because these labels
     do nothing when clicked. */
  .section-count-tooltip {
    cursor: help;
  }
  /* The superscript "i" after a column heading: the visible cue that the
     heading has a tooltip (#312). */
  .info-cue {
    margin-left: 2px;
    opacity: 0.6;
  }
  /* #323: a collapsed section's rows stay in the DOM and are hidden with
     visibility: collapse on their <tbody>, not display: none -- collapse
     removes the rows' height while their cells still count towards the
     column widths, so the table does not change width as sections open
     and close. Probed on desktop Chrome/Firefox and the HA Android app.
     Known failure case: a cell in a visible row spanning into collapsed
     rows; every rowspan here sits inside one <tbody>, which is the
     collapse unit, and panel.dom.test.ts guards that. */
  .structured-table tbody.collapsed {
    visibility: collapse;
  }
  .structured-table .section-spacer td {
    height: 24px;
    padding: 0;
    border: none;
    /* An explicit background on the co-table's spacer td: the co-table's
       per-cell tint means an untinted spacer td is already the plain :host
       background, so this is a no-op kept to avoid touching the hand-synced
       dark-mode pairs (#166). It paints the plain :host background (same
       literal #fff as :host's own default a few lines up, not a CSS var --
       this component's dark-mode override below is a hardcoded literal too,
       the dev-only :host([data-theme]) toggle needs every surface color paired
       that way, see its own comment). Dark-mode pairing lives in the dark-mode
       blocks below, not here. */
    background: #fff;
  }
  /* Three low-key tints of the same blue as --primary-color, rather than
     three unrelated hues -- keeps the section headers visually part of
     the same UI, just distinguishable from one another. */
  .structured-table tr.section-header.section-full td,
  .entity-cards .card-section-header.section-full {
    background: rgba(3, 169, 244, 0.26);
  }
  .structured-table tr.section-header.section-partial td,
  .entity-cards .card-section-header.section-partial,
  .entity-cards .card-section-header.section-in-use {
    background: rgba(3, 169, 244, 0.16);
  }
  .structured-table tr.section-header.section-orphan td,
  .entity-cards .card-section-header.section-orphan,
  .entity-cards .card-section-header.section-isolated {
    background: rgba(3, 169, 244, 0.08);
  }
  /* #320: the narrow tier's Smart Devices cards. A bordered box per
     device with a gap below; no row shading, the border separates them. */
  .entity-cards {
    display: flex;
    flex-direction: column;
    gap: 8px;
    /* Capped and centred: on a wide phone an uncapped card stretches
       until each line's button sits far from its text (live review). The
       section headers share the cap, so headers and cards line up. */
    max-width: 480px;
    margin-inline: auto;
  }
  .entity-card {
    border: 1px solid var(--divider-color, #e0e0e0);
    border-radius: 8px;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .entity-card .card-line {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 8px;
  }
  /* Mirrors the table: the Appliance side reads left to right from its
     plug button; the Unmanaged Outlet side is right-aligned with its button at
     the right edge. Subtle rules divide the device, its sockets and its
     Unmanaged Outlet. */
  .co-card .card-identity {
    padding-bottom: 6px;
    border-bottom: 1px solid var(--divider-color, rgba(127, 127, 127, 0.35));
  }
  .co-card .uo-line {
    justify-content: flex-end;
    text-align: right;
    padding-top: 6px;
    border-top: 1px solid var(--divider-color, rgba(127, 127, 127, 0.35));
  }
  .co-card .card-identity + .uo-line {
    border-top: none;
    padding-top: 0;
  }
  .co-card .uo-line .uo-text {
    flex: 1;
    text-align: right;
  }
  .co-card .uo-line .attr-list {
    list-style: none;
    padding-left: 0;
  }
  /* #329: the Appliances and Unmanaged Outlets tabs' cards below the wide tier.
     .card-header holds the Add button the table keeps in its <thead>. */
  .card-header {
    display: flex;
    justify-content: center;
    margin-bottom: 8px;
  }
  .entity-card .card-none {
    text-align: center;
  }
  /* Text docks toward its own connection button, as in the Smart Device table
     (.appl-cell is right-aligned, .uo-cell left): the Appliance card's
     button is at the right, so its text is right-aligned; the Unmanaged Outlet
     card's button is at the left, so its text is left-aligned. */
  .appliance-card .card-identity,
  .appliance-card .appliance-connection {
    justify-content: flex-end;
    text-align: right;
  }
  .uo-card .card-identity .attr-list {
    list-style: none;
    padding-left: 0;
  }
  .uo-card .uo-connection .uo-occupant-list {
    display: inline-block;
    vertical-align: top;
  }
  /* #167, dev-only: :host([data-theme]) lets the theme radios above force
     light or dark regardless of the OS/browser preference -- "light"
     forces every rule below off even when prefers-color-scheme still
     says dark (:not([data-theme="light"]) guards the media-query block
     for exactly that), and "dark" duplicates the same rules outside the
     media query so they apply unconditionally. Every rule pair below
     must stay in sync by hand -- there is no CSS construct for "this
     media query OR this attribute" in one rule. */
  @media (prefers-color-scheme: dark) {
    :host(:not([data-theme="light"])) {
      background: #1c1c1c;
      --column-tint-appliance: rgba(76, 175, 80, 0.16);
      --column-tint-uo: rgba(121, 85, 72, 0.18);
    }
    :host(:not([data-theme="light"])) .header-bar,
    :host(:not([data-theme="light"])) .structured-table thead th,
    :host(:not([data-theme="light"])) .structured-table .section-spacer td {
      background: #1c1c1c;
    }
    /* Opaque, matching the frosted pane below, so rows scrolling under the
       sticky header do not show through (#480). */
    :host(:not([data-theme="light"])) .from-names-table thead th {
      background: #2e2e2e;
    }
    /* Frosted glass for the header menu (#480): the light tint is what
       separates the pane from the near-flat dark page behind it; the blur is
       only texture. The dialogs have the same look from the
       "modal-dialog-box" surface. */
    :host(:not([data-theme="light"])) .menu-list {
      background: rgba(255, 255, 255, 0.12);
      -webkit-backdrop-filter: blur(14px);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.18);
    }
    :host(:not([data-theme="light"])) .edit-field input,
    :host(:not([data-theme="light"])) .from-names-name:not([readonly]),
    :host(:not([data-theme="light"])) .dialog-filter-input,
    :host(:not([data-theme="light"])) .edit-field select {
      background: #1c1c1c;
    }
  }
  :host([data-theme="dark"]) {
    background: #1c1c1c;
    --column-tint-appliance: rgba(76, 175, 80, 0.16);
    --column-tint-uo: rgba(121, 85, 72, 0.18);
  }
  :host([data-theme="dark"]) .header-bar,
  :host([data-theme="dark"]) .structured-table thead th,
  :host([data-theme="dark"]) .structured-table .section-spacer td {
    background: #1c1c1c;
  }
  :host([data-theme="dark"]) .from-names-table thead th {
    background: #2e2e2e;
  }
  :host([data-theme="dark"]) .menu-list {
    background: rgba(255, 255, 255, 0.12);
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.18);
  }
  :host([data-theme="dark"]) .edit-field input,
  :host([data-theme="dark"]) .from-names-name:not([readonly]),
  :host([data-theme="dark"]) .dialog-filter-input,
  :host([data-theme="dark"]) .edit-field select {
    background: #1c1c1c;
  }
`, wn = [{
	label: "Filter…",
	icon: "filter",
	action: "show_filter"
}], Tn = [{
	heading: "Tools",
	icon: "tools",
	entries: [
		{
			label: "Create Appliances from Socket names…",
			icon: "appliance",
			action: "create_appliances_from_socket_names"
		},
		{
			label: "Wall Sockets for Smart Devices…",
			icon: "uo",
			action: "assign_uos_to_smart_devices"
		},
		{
			label: "Export…",
			icon: "export",
			action: "export_state"
		}
	]
}], En = st, Dn = tt, On = (e) => v`<svg class="menu-entry-icon" viewBox="0 0 24 24" aria-hidden="true">
    <path d="${e}"></path>
  </svg>`, kn = (e, t, n, r) => v`<button
    class="menu-entry ${t ? "indented" : ""}"
    @click=${() => r.choose(e.action)}
  >
    ${On(n(e.icon))}${e.label}
  </button>`;
function An(e, t, n) {
	let { tip: r } = e;
	return v`<div class="menu-wrap">
    <button
      class="menu-btn"
      data-tip="act"
      aria-describedby=${r.id}
      aria-label="Menu"
      aria-expanded=${e.open ? "true" : "false"}
      aria-controls="header-menu"
      @click=${() => n.toggle()}
    >
      <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="${En}"></path>
      </svg></button
    >${r.desc}
    <div class="menu-list" id="header-menu" ?hidden=${!e.open}>
      ${e.topEntries.map((e) => kn(e, !1, t, n))}
      <hr class="menu-separator" />
      ${e.groups.map((e) => v`<div class="menu-group">
          <p class="menu-heading ${D("heading")}">
            ${On(t(e.icon))}${e.heading}
          </p>
          ${e.entries.map((e) => kn(e, !0, t, n))}
        </div>`)}
      <hr class="menu-separator" />
      <button class="menu-entry" @click=${() => n.openSettings()}>
        ${On(Dn)}Settings…
      </button>
    </div>
  </div>`;
}
//#endregion
//#region src/outlet-binder-panel/ha-links.ts
function jn(e, t) {
	let n = new URLSearchParams(t.search);
	return n.set("more-info-entity-id", e), n.set("more-info-view", "settings"), `${t.pathname}?${n.toString()}`;
}
//#endregion
//#region src/outlet-binder-panel/utils.ts
var j = (e) => e ?? "—", M = (e, t) => t === null ? null : e.get(t) ?? t, N = (e, t) => e.get(t) ?? j(null), Mn = (e) => e.physical_position !== null && e.physical_position !== e.position ? e.physical_position : e.position, P = (e) => e instanceof Error || typeof e == "object" && e && "message" in e && typeof e.message == "string" ? e.message : String(e), Nn = (e, t) => `${e}: ${P(t)}`, Pn = (e) => /[.!?]$/.test(e) ? e : `${e}.`, F = (e, t) => e.localeCompare(t, void 0, { numeric: !0 }), I = (e) => e.alias, Fn = "No rows match the filter.", In = "No Wall Sockets available", Ln = "No Smart device sockets available", Rn = (e, t) => {
	let n = e.toLowerCase().split(/\s+/).filter(Boolean);
	if (n.length === 0) return !0;
	let r = t.join("\n").toLowerCase();
	return n.every((e) => r.includes(e));
}, L = (e, t) => {
	e && (t && !e.open ? (e.showModal(), e.querySelector("[autofocus]")?.focus()) : !t && e.open && e.close());
}, zn = (e) => `${e} powered`, Bn = (e) => e === 1 ? "1 with an Appliance" : `${e} with Appliances`, Vn = "mac", Hn = {
	manufacturer: null,
	model: null,
	name: null,
	hw_version: null,
	sw_version: null,
	mac: null,
	area_id: null
};
function Un(e, t) {
	let n = e?.[t];
	if (!n) return Hn;
	let r = n.connections.find(([e]) => e === Vn);
	return {
		manufacturer: n.manufacturer,
		model: n.model,
		name: n.name_by_user ?? n.name,
		hw_version: n.hw_version,
		sw_version: n.sw_version,
		mac: r ? r[1].toUpperCase() : null,
		area_id: n.area_id
	};
}
var Wn = "outlet_binder", Gn = /* @__PURE__ */ new WeakMap(), Kn = (e) => {
	let t = Gn.get(e);
	if (t) return t;
	let n = /* @__PURE__ */ new Map();
	for (let { device_id: t, platform: r } of Object.values(e)) {
		if (t === null || r === Wn) continue;
		let e = n.get(t) ?? /* @__PURE__ */ new Map();
		e.set(r, (e.get(r) ?? 0) + 1), n.set(t, e);
	}
	let r = /* @__PURE__ */ new Map();
	for (let [e, t] of n) {
		let [n] = [...t].sort(([e, t], [n, r]) => r - t || e.localeCompare(n));
		n && r.set(e, n[0]);
	}
	return Gn.set(e, r), r;
};
function qn(e, t) {
	return e ? Kn(e).get(t) ?? null : null;
}
//#endregion
//#region src/outlet-binder-panel/chain-state.ts
var Jn = (e) => ({
	...e,
	gapBefore: !0
}), Yn = (e, t) => {
	let n = new Map(e.cos.map((e) => [e.co_id, e])), r = new Map(e.co_sockets.map((e) => [e.co_socket_id, e])), i = /* @__PURE__ */ new Map();
	for (let t of e.co_sockets) {
		let e = i.get(t.co_id) ?? [];
		e.push(t), i.set(t.co_id, e);
	}
	let a = (e) => {
		let i = t.co(e);
		if (i.kind !== "co_socket") return;
		let a = r.get(i.id);
		return a === void 0 ? void 0 : n.get(a.co_id);
	}, o = (e) => {
		let t = /* @__PURE__ */ new Set([e.co_id]), n = [], r = e;
		for (let e = a(r); e !== void 0; e = a(r)) {
			if (t.has(e.co_id)) return {
				ancestors: n,
				top: r,
				looped: !0
			};
			t.add(e.co_id), n.push(e), r = e;
		}
		return {
			ancestors: n,
			top: r,
			looped: !1
		};
	}, s = (e) => o(e).ancestors, c = (e) => {
		if (!e.has_plug) return !0;
		let { top: n, looped: r } = o(e);
		return r ? !1 : !n.has_plug || t.co(n).kind === "uo";
	}, l = (e) => {
		let t = /* @__PURE__ */ new Set(), r = (e) => !t.has(e.co_id) && (t.add(e.co_id), (i.get(e.co_id) ?? []).some((e) => {
			if (e.plugged_into_appliance_id !== null) return !0;
			if (e.occupant_device_id === null) return !1;
			let t = n.get(e.occupant_device_id);
			return t !== void 0 && r(t);
		}));
		return r(e);
	}, u = (e) => (i.get(e.co_id) ?? []).some((e) => e.occupant_device_id !== null), d = (e) => c(e) && l(e) ? "full" : !e.has_plug || t.co(e).kind !== "nowhere" || u(e) ? "partial" : "orphan", f = (e, t) => {
		if (t.plugged_into_appliance_id !== null) return c(e);
		if (t.occupant_device_id === null) return !1;
		let r = n.get(t.occupant_device_id);
		return r !== void 0 && d(r) === "full";
	}, ee = (e) => {
		let i = t.appliance(e);
		switch (i.kind) {
			case "uo": return !0;
			case "co_socket": {
				let e = r.get(i.id), t = e === void 0 ? void 0 : n.get(e.co_id);
				return t !== void 0 && c(t);
			}
			case "nowhere": return !1;
		}
	}, te = (n) => {
		let r = (e) => e.kind === "uo" && e.id === n.uo_id;
		return e.cos.some((e) => r(t.co(e)) && d(e) === "full") || e.appliances.some((e) => r(t.appliance(e)));
	}, p = (e) => [...i.get(e.co_id) ?? []].sort((e, t) => e.position - t.position).flatMap((e) => {
		if (e.plugged_into_appliance_id !== null || e.occupant_device_id === null) return [];
		let t = n.get(e.occupant_device_id);
		return t === void 0 ? [] : [{
			child: t,
			via: e
		}];
	}), ne = (e, t, n) => {
		if (n.has(e.co_id)) return [];
		let r = new Set(n).add(e.co_id), i = p(e).map(({ child: e, via: n }) => ({
			via: n,
			rows: ne(e, t, r)
		})).filter((e) => e.rows.length > 0), a = i.flatMap((e) => e.rows);
		return d(e) === t ? [{
			kind: "live",
			co: e,
			gapBefore: !1
		}, ...a] : a.length === 0 ? [] : [{
			kind: "copy",
			co: e,
			sockets: i.map((e) => e.via),
			gapBefore: !1
		}, ...a];
	};
	return {
		hostOf: a,
		ancestors: s,
		isPowered: c,
		reachesAppliance: l,
		bandOf: d,
		socketIsComplete: f,
		applianceIsComplete: ee,
		uoIsComplete: te,
		blocks: (n) => {
			let r = [], i = /* @__PURE__ */ new Map(), s = [...e.cos].sort((e, t) => F(I(e), I(t))), c = s.filter((e) => a(e) === void 0), l = /* @__PURE__ */ new Set(), u = (e) => {
				if (!l.has(e.co_id)) {
					l.add(e.co_id);
					for (let { child: t } of p(e)) u(t);
				}
			};
			c.forEach(u);
			for (let e of s) {
				if (l.has(e.co_id)) continue;
				let t = a(o(e).top) ?? e;
				c.push(t), u(t);
			}
			for (let e of c) {
				let a = ne(e, n, /* @__PURE__ */ new Set());
				if (a.length === 0) continue;
				let o = t.co(e), s = o.kind === "uo" ? o.id : null, c = s === null ? void 0 : i.get(s);
				if (c !== void 0) {
					c.rows.push(...a.map((e, t) => t === 0 ? Jn(e) : e));
					continue;
				}
				let l = {
					uoId: s,
					sortKey: I(e),
					rows: a
				};
				r.push(l), s !== null && i.set(s, l);
			}
			if (n === "full") {
				let n = e.appliances.flatMap((e) => {
					let n = t.appliance(e);
					return n.kind === "uo" ? [{
						appliance: e,
						uoId: n.id
					}] : [];
				}).sort((e, t) => F(e.appliance.name, t.appliance.name));
				for (let { appliance: t, uoId: a } of n) {
					let n = i.get(a);
					if (n !== void 0) {
						n.rows.push({
							kind: "direct",
							appliance: t,
							gapBefore: !0
						});
						continue;
					}
					let o = {
						uoId: a,
						sortKey: e.uos.find((e) => e.uo_id === a)?.name ?? a,
						rows: [{
							kind: "direct",
							appliance: t,
							gapBefore: !1
						}]
					};
					r.push(o), i.set(a, o);
				}
			}
			return r.sort((e, t) => F(e.sortKey, t.sortKey)).map(({ uoId: e, rows: t }) => ({
				uoId: e,
				rows: t
			}));
		}
	};
}, Xn = (e) => e.uo_id === null ? e.plugged_into_co_socket_id === null ? { kind: "nowhere" } : {
	kind: "co_socket",
	id: e.plugged_into_co_socket_id
} : {
	kind: "uo",
	id: e.uo_id
}, R = (e) => Xn(e), z = (e) => Xn(e), Zn = (e) => e.sockets_in_use > 0, Qn = (e, t) => {
	if (e.occupant_device_id === null) return null;
	let n = e.plugged_into_appliance_id === null ? t.coNames : t.applianceNames;
	return {
		id: e.occupant_device_id,
		name: n.get(e.occupant_device_id) ?? null
	};
}, $n = (e, t) => ({
	device: e.coNames.get(t.co_id) ?? t.co_id,
	socket: (e.socketsByCo.get(t.co_id) ?? []).length <= 1 ? null : t.alias
}), B = (e, t) => {
	let { device: n, socket: r } = $n(e, t);
	return r === null ? n : `${n} > ${r}`;
}, er = (e, t) => {
	let { device: n, socket: r } = $n(e, t);
	return r === null ? n : `${r} on ${n}`;
}, V = (e) => {
	let t = new Map(e.uos.map((e) => [e.uo_id, e.name])), n = new Map(e.uos.map((e) => [e.uo_id, e])), r = new Map(e.cos.map((e) => [e.co_id, e.alias])), i = new Map(e.appliances.map((e) => [e.appliance_id, e.name])), a = new Map(e.appliances.map((e) => [e.appliance_id, e])), o = /* @__PURE__ */ new Map();
	for (let t of e.co_sockets) {
		let e = o.get(t.co_id) ?? [];
		e.push(t), o.set(t.co_id, e);
	}
	let s = new Map(e.co_sockets.map((e) => [e.co_socket_id, B({
		coNames: r,
		socketsByCo: o
	}, e)])), c = /* @__PURE__ */ new Map();
	for (let t of e.cos) {
		if (t.uo_id === null) continue;
		let e = c.get(t.uo_id) ?? [];
		e.push(t), c.set(t.uo_id, e);
	}
	let l = /* @__PURE__ */ new Map();
	for (let t of e.appliances) {
		let e = z(t);
		if (e.kind !== "uo") continue;
		let n = l.get(e.id) ?? [];
		n.push(t), l.set(e.id, n);
	}
	let u = Yn(e, {
		co: R,
		appliance: z
	}), d = u.bandOf, f = (e) => d(e) === "full", ee = u.socketIsComplete, te = u.applianceIsComplete, p = u.uoIsComplete;
	return {
		uoNames: t,
		uosById: n,
		coNames: r,
		cosById: new Map(e.cos.map((e) => [e.co_id, e])),
		coSocketLabels: s,
		socketsById: new Map(e.co_sockets.map((e) => [e.co_socket_id, e])),
		applianceNames: i,
		appliancesById: a,
		socketsByCo: o,
		cosByUo: c,
		appliancesByUo: l,
		chain: u,
		coBand: d,
		coIsFullyChained: f,
		socketIsFullyChained: ee,
		applianceIsFullyChained: te,
		uoIsFullyChained: p
	};
}, H = [
	"appliances",
	"devices",
	"uos"
], tr = {
	devices: "Smart Devices",
	appliances: "Appliances",
	uos: "Wall Sockets"
}, nr = (e) => e >= 1320 ? "wide" : e >= 780 ? "medium" : "narrow", rr = (e) => `· ${e} match`, ir = (e, t, n = null) => n === null ? `${tr[e]} (${t})` : `${tr[e]} (${t}) ${rr(n)}`, ar = (e, t) => {
	let n = H.indexOf(e), r = H.length;
	switch (t) {
		case "ArrowRight": return H[(n + 1) % r];
		case "ArrowLeft": return H[(n - 1 + r) % r];
		case "Home": return H[0];
		case "End": return H[r - 1];
		default: return null;
	}
}, or = (e, t, n, r = 8) => {
	let i = (e, t, n) => Math.max(r, Math.min(e, n - r - t));
	return {
		left: i(e.left, t.width, n.width),
		top: i(e.top, t.height, n.height)
	};
}, sr = (e, t) => ({
	dx: e.x - t.left,
	dy: e.y - t.top
}), cr = (e, t) => ({
	left: e.x - t.dx,
	top: e.y - t.dy
}), lr = (e, t, n, r) => {
	let i = or(e, t, n);
	return {
		left: i.left - r.left,
		top: i.top - r.top
	};
}, ur = (e, t, n) => ({
	kind: e,
	id: t,
	...n,
	savedDraft: { ...n.draft },
	saving: !1,
	error: null,
	haItemsOpen: !1
}), dr = (e) => Object.entries(e.draft).some(([t, n]) => e.savedDraft[t] !== n), fr = (e, t) => e === null ? null : {
	...e,
	saving: !1,
	error: P(t)
}, pr = (e, t) => {
	let n = e.uosById.get(t);
	return n === void 0 ? null : {
		kind: "uo",
		entity: n
	};
}, U = (e, t) => {
	let n = e.cosById.get(t);
	return n === void 0 ? null : {
		kind: "co",
		entity: n
	};
}, mr = (e, t) => {
	let n = e.appliancesById.get(t);
	return n === void 0 ? null : {
		kind: "appliance",
		entity: n
	};
}, hr = (e, t) => {
	let n = e.socketsById.get(t);
	return n === void 0 ? null : U(e, n.co_id);
}, gr = (e, t) => e.plugged_into_appliance_id === null ? e.occupant_device_id === null ? null : U(t, e.occupant_device_id) : mr(t, e.plugged_into_appliance_id), _r = {
	name: "name",
	alias: "alias",
	location_note: "location note",
	appliance_type: "type",
	description: "description",
	location_override_ha_area_id: "HA area",
	location_override_location_note: "override note",
	socket_type: "type",
	ha_area_id: "HA area",
	socket_count: "sockets"
}, vr = /* @__PURE__ */ new Map([["ha_area_id", "— none —"], ["location_override_ha_area_id", "— inherit —"]]), yr = "Areas are defined in Home Assistant, not in Outlet Binder.", br = /* @__PURE__ */ new Set(["socket_count"]), xr = /^\s*-?\d+\s*$/, Sr = (e) => {
	let t = wr[e.kind].requiredField;
	return (e.draft[t] ?? "").trim() !== "" && Object.entries(e.draft).every(([e, t]) => !br.has(e) || xr.test(t));
}, Cr = (e) => {
	let t = wr[e.kind], n = {
		type: t.wsType,
		[t.idField]: e.id
	};
	for (let [r, i] of Object.entries(e.draft)) n[r] = br.has(r) ? Number(i) : r === t.requiredField ? i : i.trim() === "" ? null : i;
	for (let [t, r] of Object.entries(e.passthrough)) n[t] = r;
	return n;
}, W = {
	uo: "Wall Socket",
	appliance: "Appliance",
	co: "Smart Device",
	co_socket: "Socket"
}, wr = {
	uo: {
		wsType: "outlet_binder/update_uo",
		idField: "uo_id",
		requiredField: "name"
	},
	appliance: {
		wsType: "outlet_binder/update_appliance",
		idField: "appliance_id",
		requiredField: "name"
	},
	co: {
		wsType: "outlet_binder/update_co",
		idField: "co_id",
		requiredField: "alias"
	},
	co_socket: {
		wsType: "outlet_binder/update_co_socket",
		idField: "co_socket_id",
		requiredField: "alias"
	}
}, Tr = {
	uo: {
		wsType: "outlet_binder/delete_uo",
		idField: "uo_id"
	},
	appliance: {
		wsType: "outlet_binder/delete_appliance",
		idField: "appliance_id"
	},
	co: {
		wsType: "outlet_binder/delete_co",
		idField: "co_id"
	}
}, Er = {
	uo: {
		wsType: "outlet_binder/create_uo",
		requiredField: "name"
	},
	appliance: {
		wsType: "outlet_binder/create_appliance",
		requiredField: "name"
	}
}, Dr = {
	uo: {
		name: "",
		location_note: "",
		ha_area_id: ""
	},
	appliance: {
		name: "",
		appliance_type: "",
		description: ""
	}
}, Or = (e) => ({
	draft: {
		name: e.name,
		ha_area_id: e.ha_area_id ?? "",
		location_note: e.location_note ?? "",
		socket_count: String(e.socket_count)
	},
	passthrough: {},
	pluggedIntoHaDevice: null,
	titleHaDevice: null,
	readonlyFields: [["sockets in use", String(e.sockets_in_use)]]
}), kr = "Socket's HA name", Ar = (e) => [kr, e === void 0 ? "…" : j(e)], jr = (e, t) => {
	let n = z(e);
	switch (n.kind) {
		case "co_socket": return {
			text: N(t.coSocketLabels, n.id),
			target: hr(t, n.id)
		};
		case "uo": return {
			text: N(t.uoNames, n.id),
			target: pr(t, n.id)
		};
		case "nowhere": return null;
	}
}, Mr = (e, t, n) => {
	let r = z(e);
	return {
		draft: {
			name: e.name,
			appliance_type: e.type ?? "",
			description: e.description ?? ""
		},
		passthrough: {},
		pluggedInto: jr(e, t),
		pluggedIntoHaDevice: r.kind === "co_socket" ? t.socketsById.get(r.id)?.co_id ?? null : null,
		titleHaDevice: null,
		readonlyFields: [Ar(n)]
	};
}, Nr = (e, t, n) => {
	if (!e.has_plug) return "---> —";
	if (R(e).kind === "nowhere") return "---> unplugged";
	let r = e.inherited_ha_area_source_id;
	if (r === null) return "---> —";
	let i = (e) => j(M(n, e)), a = t.uosById.get(r);
	if (a) return `---> ${a.name} : ${i(a.ha_area_id)}`;
	let o = t.cosById.get(r);
	return o ? `---> ${o.alias} : ${i(o.location_override?.ha_area_id ?? null)}` : "---> —";
}, Pr = (e, t, n) => {
	let r = R(e), i = r.kind === "co_socket" ? t.socketsById.get(r.id) : void 0;
	return {
		draft: {
			alias: e.alias,
			location_override_ha_area_id: e.location_override?.ha_area_id ?? "",
			location_override_location_note: e.location_override?.location_note ?? ""
		},
		passthrough: {},
		inheritLabel: Nr(e, t, n),
		pluggedInto: r.kind === "uo" ? {
			text: M(t.uoNames, r.id) ?? r.id,
			target: pr(t, r.id)
		} : r.kind === "co_socket" ? i ? {
			text: B(t, i),
			target: U(t, i.co_id)
		} : {
			text: j(null),
			target: null
		} : null,
		pluggedIntoHaDevice: i?.co_id ?? null,
		titleHaDevice: e.co_id,
		readonlyFields: [["all on/off entity", j(e.all_on_off_entity_registry_id)], ["created at", e.created_at]]
	};
}, Fr = (e, t) => {
	let n = Qn(e, t);
	return {
		draft: {
			alias: e.alias,
			socket_type: e.socket_type ?? ""
		},
		passthrough: { physical_position: e.physical_position },
		pluggedInto: n === null ? null : {
			text: j(n.name),
			target: gr(e, t)
		},
		pluggedIntoHaDevice: n !== null && e.plugged_into_appliance_id === null ? n.id : null,
		titleHaDevice: e.co_id,
		readonlyFields: [
			["smart device", j(M(t.coNames, e.co_id))],
			["position", String(e.position)],
			["monitoring entity", j(e.monitoring_entity_registry_id)]
		]
	};
}, Ir = 4, G = 8;
function Lr(e, t, n) {
	return n < t ? t : Math.min(Math.max(e, t), n);
}
function Rr(e, t, n, r = null) {
	let i = n.height - (e.top + e.height) - Ir, a = e.top - Ir, o = t.height + G <= i, s = t.height + G <= a, c = o || !s && i >= a ? e.top + e.height + Ir : e.top - Ir - t.height, l = r === null ? null : r.left - Ir - t.width;
	return {
		left: Lr(l !== null && l >= G ? l : e.left, G, n.width - t.width - G),
		top: Lr(c, G, n.height - t.height - G)
	};
}
function zr(e) {
	let { event: t, pointerType: n, lastInput: r, host: i } = e;
	if (t === "escape") return "hide";
	if (t === "click") return i === "info" && n === "touch" ? "toggle" : "hide";
	if (i === null) return "ignore";
	switch (t) {
		case "pointerover": return n === "touch" ? "ignore" : "showDelayed";
		case "pointerout":
		case "focusout": return "hide";
		case "focusin": return r === "keyboard" ? "show" : "ignore";
	}
}
var Br = /^(- |\d+\. )/;
function Vr(e) {
	let t = e.indexOf("\n\n");
	return t >= 0 ? {
		title: e.slice(0, t),
		body: e.slice(t + 2)
	} : Br.test(e) ? {
		title: "",
		body: e
	} : {
		title: e,
		body: ""
	};
}
function Hr(e) {
	return e.split("\n").map((e) => {
		let t = Br.exec(e);
		return t ? {
			kind: "item",
			marker: t[1].trim(),
			text: e.slice(t[1].length)
		} : e.startsWith("    ") ? {
			kind: "cont",
			marker: "",
			text: e.trimStart()
		} : {
			kind: "plain",
			marker: "",
			text: e
		};
	});
}
var Ur = [
	"appliance",
	"co",
	"uo"
], Wr = (e) => Ur.includes(e), Gr = {
	...W,
	co_socket: "Smart Socket"
}, Kr = {
	appliance: "appliance",
	co: "co",
	co_socket: "co",
	uo: "uo"
}, qr = (e, t, n) => ({
	icon: e,
	title: t,
	action: n.action ?? "",
	blocked: n.blocked ?? !1,
	attrs: n.attrs ?? []
}), K = (e, t, n = {}) => qr(Kr[e], `${Gr[e]}: ${t}`, n), Jr = (e, t = {}) => qr(null, e, t), Yr = "- ", Xr = (e) => e.replace(/[\t\r\n]+/g, " "), Zr = (e) => {
	let t = (e.action === "" ? [e.title] : [e.title, e.action]).map(Xr), n = e.attrs.flatMap((e) => [`${Xr(e.label)}:\t${Xr(e.value)}`, ...(e.items ?? []).map((e) => `${Yr}${Xr(e)}`)]);
	return [t.join("\n"), ...n.length > 0 ? [n.join("\n")] : []].join("\n\n");
}, Qr = (e, t, n) => {
	let r = e.indexOf("\n\n"), i = (r >= 0 ? e.slice(0, r) : e).split("\n"), a = [];
	if (r >= 0) for (let t of e.slice(r + 2).split("\n")) {
		let e = a.at(-1);
		if (t.startsWith(Yr) && e !== void 0) {
			e.items.push(t.slice(2));
			continue;
		}
		let n = t.indexOf(":	");
		a.push(n >= 0 ? {
			label: t.slice(0, n),
			value: t.slice(n + 2),
			items: []
		} : {
			label: "",
			value: t,
			items: []
		});
	}
	return {
		icon: t,
		title: i[0] ?? "",
		action: i[1] ?? "",
		blocked: n,
		attrs: a.map(({ items: e, ...t }) => e.length > 0 ? {
			...t,
			items: e
		} : t)
	};
}, $r = {
	system: "Auto",
	light: "Light",
	dark: "Dark"
}, ei = "system", ti = "outlet-binder-panel:theme-override", ni = () => {
	try {
		let e = localStorage.getItem(ti);
		return e !== null && Object.hasOwn($r, e) ? e : ei;
	} catch {
		return ei;
	}
}, ri = "outlet-binder-panel:seen-cos", ii = () => {
	let e;
	try {
		e = localStorage.getItem(ri);
	} catch {
		return null;
	}
	if (e === null) return null;
	try {
		return JSON.parse(e);
	} catch {
		return {};
	}
}, ai = (e) => {
	try {
		localStorage.setItem(ri, JSON.stringify(e));
	} catch {}
}, oi = (e, t, n) => {
	let r = t === null, i = t ?? {}, a = /* @__PURE__ */ new Set(), o = {};
	for (let t of e) {
		let e = i[t.co_id], s = e && e.createdAt === t.created_at ? e : {
			createdAt: t.created_at,
			firstSeenAt: r ? 0 : n
		};
		o[t.co_id] = s, n - s.firstSeenAt < 6e5 && a.add(t.co_id);
	}
	return {
		newIds: a,
		nextSeen: o
	};
}, si = (e) => z(e).kind === "nowhere", ci = (e) => !Zn(e), li = (e, t) => e.name.localeCompare(t.name), ui = (e) => {
	let t = [], n = [];
	for (let r of e.appliances) (si(r) ? t : n).push(r);
	return {
		isolated: t.sort(li),
		inUse: n.sort(li)
	};
}, di = (e) => {
	let t = [], n = [];
	for (let r of e.uos) (ci(r) ? t : n).push(r);
	return {
		isolated: t.sort(li),
		inUse: n.sort(li)
	};
}, fi = {
	full: "Appliance → Smart Socket → Wall Socket",
	partial: "Appliance → Smart Socket OR Smart Socket → Wall Socket",
	orphan: "Unconnected Smart Socket"
}, pi = [
	"full",
	"partial",
	"orphan"
], mi = "outlet-binder-panel:collapsed-sections", hi = () => {
	try {
		let e = localStorage.getItem(mi);
		if (e === null) return /* @__PURE__ */ new Set();
		let t = JSON.parse(e);
		return Array.isArray(t) ? new Set(t.filter((e) => pi.includes(e))) : /* @__PURE__ */ new Set();
	} catch {
		return /* @__PURE__ */ new Set();
	}
}, gi = (e) => {
	try {
		localStorage.setItem(mi, JSON.stringify([...e]));
	} catch {}
}, _i = {
	isolated: "Isolated",
	in_use: "In use"
}, vi = ["isolated", "in_use"], yi = "outlet-binder-panel:collapsed-side-sections", bi = () => ({
	appliance: /* @__PURE__ */ new Set(["in_use"]),
	uo: /* @__PURE__ */ new Set(["in_use"])
}), xi = () => {
	try {
		let e = localStorage.getItem(yi);
		if (e === null) return bi();
		let t = JSON.parse(e);
		if (typeof t != "object" || !t) return bi();
		let n = t, r = bi(), i = (e) => {
			let t = n[e];
			return Array.isArray(t) ? new Set(t.filter((e) => vi.includes(e))) : r[e];
		};
		return {
			appliance: i("appliance"),
			uo: i("uo")
		};
	} catch {
		return bi();
	}
}, Si = (e) => {
	try {
		localStorage.setItem(yi, JSON.stringify({
			appliance: [...e.appliance],
			uo: [...e.uo]
		}));
	} catch {}
}, Ci = "outlet-binder-panel:active-tab", wi = () => {
	try {
		let e = localStorage.getItem(Ci);
		return H.includes(e) ? e : "devices";
	} catch {
		return "devices";
	}
}, Ti = (e) => {
	try {
		localStorage.setItem(Ci, e);
	} catch {}
}, Ei = (e, t) => {
	let n = e.plugged_into_appliance_id;
	return n === null ? e.occupant_device_id === null ? {
		appliance: void 0,
		co: void 0,
		name: ""
	} : {
		appliance: void 0,
		co: t.cosById.get(e.occupant_device_id),
		name: j(t.coNames.get(e.occupant_device_id))
	} : {
		appliance: t.appliancesById.get(n),
		co: void 0,
		name: j(M(t.applianceNames, n))
	};
}, Di = (e, t) => {
	let n = R(e);
	if (n.kind !== "co_socket") return null;
	let r = t.socketsById.get(n.id), i = r === void 0 ? void 0 : t.cosById.get(r.co_id);
	return r === void 0 || i === void 0 ? null : (t.socketsByCo.get(i.co_id) ?? []).length > 1 ? `${i.alias} Socket ${Mn(r)}` : i.alias;
}, Oi = (e, t) => {
	let n = Di(e, t);
	return n === null ? null : `In: ${n}`;
}, ki = (e, t) => {
	let n = t.chain.ancestors(e).at(-1) ?? e;
	if (!n.has_plug) return n.alias;
	let r = R(n);
	return r.kind === "uo" ? t.uoNames.get(r.id) ?? null : null;
}, Ai = (e, t) => e.has_plug ? ki(e, t) : null, ji = (e, t) => `${j(e)}: ${j(t)}`, Mi = "View/Edit", Ni = (e) => K("co", e.name, {
	action: Mi,
	attrs: [
		{
			label: "Model",
			value: `${j(e.integration)} : ${j(e.model)}`
		},
		...e.uoName === null ? [] : [{
			label: "In",
			value: ji(e.uoName, e.effectiveArea)
		}],
		{
			label: "Area",
			value: j(e.deviceArea)
		}
	]
}), Pi = (e) => K("appliance", e.name, {
	action: Mi,
	attrs: [
		{
			label: "Type",
			value: j(e.type)
		},
		{
			label: "Plugged into",
			value: e.pluggedInto ?? "Not plugged in"
		},
		...e.uoName === null ? [] : [{
			label: "In",
			value: ji(e.uoName, e.effectiveArea)
		}],
		...e.description ? [{
			label: "Description",
			value: e.description
		}] : []
	]
}), Fi = (e) => K("uo", e.name, {
	action: Mi,
	attrs: [
		{
			label: "Area",
			value: j(e.area)
		},
		...e.note ? [{
			label: "Note",
			value: e.note
		}] : [],
		{
			label: "Sockets",
			value: `${e.socketsInUse} of ${e.socketCount} in use`
		}
	]
}), Ii = (e, t, n) => {
	if ((n.socketsByCo.get(e.co_id) ?? []).length < 2) return e.alias;
	let r = t.map(Mn).sort((e, t) => e - t);
	return `${e.alias} ${r.length === 1 ? "Socket" : "Sockets"} ${r.join(", ")}`;
}, Li = (e, t) => t.coBand(e), Ri = (e, t) => {
	let n = z(e);
	switch (n.kind) {
		case "co_socket": {
			let e = t.socketsById.get(n.id), r = e ? t.cosById.get(e.co_id) : void 0;
			return e && r ? {
				kind: "co_socket",
				co: r,
				socket: e
			} : null;
		}
		case "uo": {
			let e = t.uosById.get(n.id);
			return e ? {
				kind: "uo",
				uo: e
			} : null;
		}
		case "nowhere": return null;
	}
}, zi = (e, t) => [...t.cosByUo.get(e.uo_id) ?? []].sort((e, t) => F(I(e), I(t))), Bi = (e, t) => [...t.appliancesByUo.get(e.uo_id) ?? []].sort(li), Vi = (e) => ({
	full: e.chain.blocks("full"),
	partial: e.chain.blocks("partial"),
	orphan: e.chain.blocks("orphan")
}), Hi = () => ({
	appliance: 0,
	co: 0,
	coReadyNotPowered: 0,
	coNoConsumersButPowered: 0,
	uo: 0,
	socketTotal: 0,
	socketInUse: 0
}), Ui = (e, t) => {
	let n = {
		full: Hi(),
		partial: Hi(),
		orphan: Hi()
	};
	for (let r of e.appliances) si(r) ? n.orphan.appliance += 1 : t.applianceIsFullyChained(r) ? n.full.appliance += 1 : n.partial.appliance += 1;
	for (let r of e.cos) {
		let e = t.socketsByCo.get(r.co_id) ?? [], i = Li(r, t);
		if (n[i].socketTotal += e.length, n[i].socketInUse += e.filter((e) => e.occupant_device_id !== null).length, i === "full") {
			n.full.co += 1;
			continue;
		}
		if (i === "orphan") {
			n.orphan.co += 1;
			continue;
		}
		n.partial.co += 1, t.chain.isPowered(r) ? n.partial.coNoConsumersButPowered += 1 : n.partial.coReadyNotPowered += 1;
	}
	for (let r of e.uos) ci(r) ? n.orphan.uo += 1 : t.uoIsFullyChained(r) ? n.full.uo += 1 : n.partial.uo += 1;
	return n;
}, Wi = (e, t) => {
	let n = `${t.socketTotal}, ${Bn(t.socketInUse)}`;
	switch (e) {
		case "orphan": return [{
			label: "Devices",
			value: String(t.co)
		}, {
			label: "Sockets",
			value: String(t.socketTotal)
		}];
		case "partial": return [
			{
				label: "Devices",
				value: `${t.co}, ${zn(t.coNoConsumersButPowered)}`
			},
			{
				label: "Sockets",
				value: n
			},
			{
				label: "Wall Sockets",
				value: String(t.uo)
			}
		];
		case "full": return [
			{
				label: "Devices",
				value: String(t.co)
			},
			{
				label: "Sockets",
				value: n
			},
			{
				label: "Wall Sockets",
				value: String(t.uo)
			}
		];
	}
}, Gi = "Clear the filter to collapse sections", Ki = (e, t) => e ? "filtering" : t ? "expand" : "collapse", qi = {
	collapse: "Collapse",
	expand: "Expand",
	info: ""
}, Ji = (e, t, n) => n === "filtering" ? Jr(Gi, { attrs: t }) : Jr(e, {
	action: qi[n],
	attrs: t
}), Yi = (e, t, n) => Ji(fi[e], Wi(e, t), n), Xi = {
	appliance: "Appliances",
	uo: "Wall Sockets"
}, Zi = (e, t, n, r) => Ji(`${_i[t]} ${Xi[e]}`, [{
	label: "Count",
	value: String(n)
}], r), Qi = (e, t) => {
	switch (e) {
		case "appliance": return Jr("Appliances", {
			action: "Plugged in to a Smart Socket",
			attrs: [{
				label: "All Appliances",
				value: String(t.appliances)
			}]
		});
		case "co": return Jr("Smart devices & Sockets", {
			action: "Smart plugs and power strips, and the switchable Sockets on each",
			attrs: [{
				label: "Devices",
				value: String(t.cos)
			}, {
				label: "Sockets",
				value: `${t.socketTotal}, ${Bn(t.socketInUse)}`
			}]
		});
		case "uo": return Jr("Wall Sockets", {
			action: "Where your Smart devices are plugged in",
			attrs: [{
				label: "All Wall Sockets",
				value: String(t.uos)
			}]
		});
	}
}, $i = (e, t, n) => `${e} ${e === 1 ? t : n}`, ea = (e, t) => {
	let n = e.area_id ? t.areas?.[e.area_id] : void 0;
	return {
		area: n,
		floor: n?.floor_id ? t.floors?.[n.floor_id] : void 0
	};
}, ta = (e, t, n, r) => {
	let i = Un(r.devices, e.co_id), { area: a, floor: o } = ea(i, r), s = n.filter((e) => e.monitoring_entity_registry_id !== null).map((e) => String(Mn(e)));
	return {
		coId: e.co_id,
		title: {
			text: e.alias,
			target: {
				kind: "co",
				entity: e
			}
		},
		fields: [
			["device name", i.name],
			["make and model", i.manufacturer === null && i.model === null ? null : `${j(i.manufacturer)}:${j(i.model)}`],
			["MAC address", i.mac],
			["hardware version", i.hw_version],
			["software version", i.sw_version],
			["area", a?.name ?? null],
			["floor", o?.name ?? null],
			["Wall Socket", R(e).kind === "nowhere" ? "Not linked yet" : "Linked"],
			["Sockets", String(n.length)],
			["reporting power", s.length > 0 ? s.join(", ") : "None"],
			["all on/off", e.all_on_off_entity_registry_id === null ? "No" : "Yes"],
			["integration", t.integration_domain],
			["pattern", t.pattern_id]
		]
	};
}, na = (e, t, n) => {
	let r = new Map(t.cos.map((e) => [e.co_id, e])), i = [], a = 0;
	for (let o of e) {
		let e = r.get(o.co_id);
		if (!e) continue;
		let s = t.co_sockets.filter((t) => t.co_id === e.co_id).sort((e, t) => e.position - t.position);
		a += s.length, i.push(ta(e, o, s, n));
	}
	return i.length === 0 ? null : (i.sort((e, t) => F(e.title.text, t.title.text)), {
		heading: `Found ${$i(i.length, "new Smart Device", "new Smart Devices")} with ${$i(a, "Socket", "Sockets")}`,
		entries: i
	});
}, ra = (e) => e.trim() !== "", ia = "powering", aa = "holding", oa = (e, t) => `${e}: ${j(t)}`, sa = (e, t) => [["HA area", t], ["location note", e.location_note]], ca = (e, t) => [e.name, ...sa(e, t.uoArea(e)).map(([e, t]) => oa(e, t))], la = (e, t) => t === "table" ? `(${j(e.manufacturer)}:${j(e.model)})` : `(${j(e.manufacturer)} : ${j(e.model)})`, ua = (e, t) => (t.socketsByCo.get(e.co_id) ?? []).map((e) => Ei(e, t).name), da = (e, t) => [
	e.alias,
	la(t.coModel(e), "table"),
	Di(e, t.h) ?? "",
	...ua(e, t.h)
], fa = (e, t, n) => {
	let r = e === null ? null : Oi(e, n.h);
	return e !== null && r !== null ? [r, ki(e, n.h) ?? ""] : t === null ? [] : ca(t, n);
}, pa = (e, t, n) => [
	e.alias,
	la(n.coModel(e), "cards"),
	...ua(e, n.h),
	...fa(e, t, n)
], ma = (e, t, n, r) => {
	switch (e.kind) {
		case "live": return n === "table" ? da(e.co, r) : pa(e.co, t, r);
		case "copy": return n === "table" ? [Ii(e.co, e.sockets, r.h)] : [];
		case "direct": return n === "table" ? [e.appliance.name] : [e.appliance.name, ...fa(null, t, r)];
	}
}, ha = (e, t, n) => {
	let r = e.uoId === null ? null : n.h.uosById.get(e.uoId) ?? null;
	return [...t === "table" && r !== null ? ca(r, n) : [], ...e.rows.flatMap((e) => ma(e, r, t, n))];
}, ga = (e, t) => `${e}:${t}`, _a = (e, t) => {
	let n = Ri(e, t);
	return n === null ? null : n.kind === "co_socket" ? {
		name: n.co.alias,
		suffix: `: ${Mn(n.socket)}`
	} : {
		name: n.uo.name,
		suffix: null
	};
}, va = (e, t) => {
	let n = _a(e, t);
	return [e.name, ...n === null ? [] : [
		"in",
		n.name,
		n.suffix ?? ""
	]];
}, ya = (e, t) => {
	let n = zi(e, t.h), r = Bi(e, t.h);
	return [
		...ca(e, t),
		...n.length === 0 ? [] : [ia, ...n.map((e) => e.alias)],
		...r.length === 0 ? [] : [aa, ...r.map((e) => e.name)]
	];
}, ba = (e, t, n, r, i, a) => {
	let o = (t) => !ra(e) || Rn(e, t()), s = /* @__PURE__ */ new Set(), c = 0;
	for (let [e, n] of Object.entries(t)) n.forEach((t, n) => {
		o(() => ha(t, i, a)) && (s.add(ga(e, n)), c += t.rows.filter((e) => e.kind !== "copy").length);
	});
	let l = new Set(n.filter((e) => o(() => va(e, a.h))).map((e) => e.appliance_id)), u = new Set(r.filter((e) => o(() => ya(e, a))).map((e) => e.uo_id));
	return {
		filtering: ra(e),
		blocks: s,
		appliances: l,
		uos: u,
		counts: {
			devices: c,
			appliances: l.size,
			uos: u.size
		}
	};
}, xa = {
	uk: bt,
	eu: gt,
	us: xt,
	de: ht,
	fr: _t,
	it: vt,
	jp: yt,
	au: pt,
	ch: mt
};
//#endregion
//#region src/outlet-binder-panel/area-picker.ts
function Sa(e, t) {
	let n = new Map(t.map((e) => [e.floor_id, e])), r = /* @__PURE__ */ new Map(), i = [];
	for (let t of e) {
		let e = {
			area_id: t.area_id,
			name: t.name
		};
		if (t.floor_id !== null && n.has(t.floor_id)) {
			let n = r.get(t.floor_id) ?? [];
			n.push(e), r.set(t.floor_id, n);
		} else i.push(e);
	}
	let a = [...r.entries()].map(([e, t]) => ({
		floor: n.get(e),
		options: [...t].sort((e, t) => e.name.localeCompare(t.name))
	})).sort((e, t) => e.floor.level === null && t.floor.level === null ? e.floor.name.localeCompare(t.floor.name) : e.floor.level === null ? 1 : t.floor.level === null ? -1 : e.floor.level === t.floor.level ? e.floor.name.localeCompare(t.floor.name) : e.floor.level - t.floor.level).map(({ floor: e, options: t }) => ({
		label: e.name,
		options: t
	}));
	return i.length === 0 ? a : (i.sort((e, t) => e.name.localeCompare(t.name)), [...a, {
		label: null,
		options: i
	}]);
}
function Ca(e) {
	return new Map(e.map((e) => [e.area_id, e.name]));
}
function wa(e, t) {
	let n = Object.values(e ?? {});
	return {
		groups: Sa(n, Object.values(t ?? {})),
		names: Ca(n)
	};
}
var Ta = { kind: "none" }, Ea = (e, t) => e === null || e === t, Da = (e, t, n) => {
	let r = e.cos.filter((e) => e.has_plug && R(e).kind === "nowhere").map((e) => {
		let r = t(e.co_id), i = r === null ? null : n.get(r) ?? null;
		return {
			coId: e.co_id,
			label: e.alias,
			areaId: i === null ? null : r,
			areaName: i
		};
	}), i = (e) => e.areaName ?? "￿";
	return r.sort((e, t) => F(i(e), i(t)) || F(e.label, t.label) || e.coId.localeCompare(t.coId));
}, Oa = (e) => e ?? "No room in HA", ka = (e) => e.label, Aa = (e) => [Oa(e.areaName), ka(e)], ja = (e, t, n) => e.filter((e) => J(t, e).kind !== "none" || Rn(n, Aa(e))), Ma = (e) => {
	let t = [];
	for (let n of e) {
		let e = t[t.length - 1];
		e && e.areaId === n.areaId ? e.rows.push(n) : t.push({
			areaId: n.areaId,
			areaName: n.areaName,
			rows: [n]
		});
	}
	return t;
}, q = (e, t) => t[e.coId] ?? e.areaName ?? e.label, Na = "\0", Pa = (e) => {
	switch (e.kind) {
		case "none": return "none";
		case "new": return "new";
		case "existing": return `existing${Na}${e.uoId}`;
	}
}, Fa = (e) => {
	let [t, n] = e.split(Na);
	return t === "new" ? { kind: "new" } : t === "existing" && n ? {
		kind: "existing",
		uoId: n
	} : Ta;
}, J = (e, t) => e[t.coId] ?? Ta, Ia = (e, t, n) => {
	let r = [], i = t.uos.filter((t) => Ea(e.areaId, t.ha_area_id)).sort((e, t) => F(e.name, t.name) || e.uo_id.localeCompare(t.uo_id));
	for (let t of i) {
		let i = e.areaId === null && t.ha_area_id !== null ? n.get(t.ha_area_id) : void 0;
		r.push({
			value: Pa({
				kind: "existing",
				uoId: t.uo_id
			}),
			label: i === void 0 ? t.name : `${t.name} (${i})`
		});
	}
	return r;
}, La = (e) => e.trim() === "", Ra = (e, t, n) => new Set(e.filter((e) => J(t, e).kind === "new" && La(q(e, n))).map((e) => e.coId)), Y = (e) => e.trim().replace(/ /g, "_").replace(/[A-Z]/g, (e) => e.toLowerCase()), za = (e, t, n, r) => {
	let i = new Set(r.map((e) => Y(e.name))), a = e.filter((e) => J(t, e).kind === "new" && !La(q(e, n))).map((e) => ({
		coId: e.coId,
		key: Y(q(e, n))
	})), o = /* @__PURE__ */ new Map();
	for (let { key: e } of a) o.set(e, (o.get(e) ?? 0) + 1);
	let s = /* @__PURE__ */ new Map();
	for (let { coId: e, key: t } of a) i.has(t) ? s.set(e, "existing") : (o.get(t) ?? 0) > 1 && s.set(e, "new");
	return s;
}, Ba = (e, t, n, r) => {
	let i = new Set(r.map((e) => Y(e.name)));
	for (let r of e) {
		let e = q(r, n);
		J(t, r).kind === "new" && !La(e) && i.add(Y(e));
	}
	let a = {};
	for (let r of e) {
		if (J(t, r).kind !== "none") continue;
		let e = q(r, n);
		La(e) || i.has(Y(e)) || (i.add(Y(e)), a[r.coId] = { kind: "new" });
	}
	return {
		...t,
		...a
	};
}, Va = (e, t) => e.filter((e) => J(t, e).kind !== "none").length, Ha = (e, t, n) => {
	let r = [], i = [];
	for (let a of e) {
		let e = J(t, a);
		switch (e.kind) {
			case "none": break;
			case "new":
				r.push({
					coId: a.coId,
					label: a.label,
					name: q(a, n).trim(),
					areaId: a.areaId
				}), i.push({
					coId: a.coId,
					label: a.label,
					target: { kind: "created" }
				});
				break;
			case "existing": i.push({
				coId: a.coId,
				label: a.label,
				target: {
					kind: "existing",
					uoId: e.uoId
				}
			});
		}
	}
	return {
		creates: r,
		assigns: i
	};
}, Ua = () => ({
	choices: {},
	edits: {},
	filter: "",
	saving: !1,
	failures: []
}), Wa = (e, t, n) => ({
	...e,
	choices: {
		...e.choices,
		[t]: n
	}
}), Ga = (e, t) => (e.choices[t] ?? Ta).kind === "none" ? { kind: "new" } : Ta, Ka = (e, t) => ({
	...e,
	choices: t
}), qa = (e, t) => ({
	...e,
	filter: t
}), Ja = (e, t, n) => ({
	...e,
	edits: {
		...e.edits,
		[t]: n
	}
}), Ya = (e) => ({
	...e,
	saving: !0,
	failures: []
}), Xa = (e, t) => ({
	...e,
	choices: {},
	saving: !1,
	failures: t
}), Za = at, Qa = et, $a = rt, eo = (e, t) => {
	let { tip: n, closeTip: r } = e;
	return v`<div class="main-filter-wrap">
      <button
        type="button"
        class="main-filter-open"
        data-tip="act"
        aria-describedby=${n.id}
        aria-label="Filter"
        aria-expanded=${e.open ? "true" : "false"}
        aria-controls="main-filter"
        @click=${() => t.show()}
      >
        <svg class="menu-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="${Za}"></path>
        </svg></button
      >${n.desc}
      <div
        class="menu-list main-filter"
        id="main-filter"
        ?hidden=${!e.open}
        style=${e.pos ? `left: ${e.pos.left}px; top: ${e.pos.top}px; right: auto; margin-top: 0;` : ""}
      >
        <div
          class="main-filter-handle"
          @pointerdown=${(e) => t.startDrag(e)}
          @pointermove=${(e) => t.moveDrag(e)}
          @pointerup=${() => t.endDrag()}
          @pointercancel=${() => t.endDrag()}
        >
          <svg class="menu-entry-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="${$a}"></path>
          </svg>
        </div>
        <div class="main-filter-row">
        <input
          type="search"
          class="dialog-filter-input main-filter-input"
          aria-label="Filter the main screen"
          placeholder="Filter…"
          .value=${e.text}
          @input=${(e) => {
		t.setText(e.target.value);
	}}
          @keydown=${(e) => {
		e.key === "Escape" && (e.preventDefault(), t.close());
	}}
        /><button
          type="button"
          class="main-filter-close"
          data-tip="act"
          aria-describedby=${r.id}
          aria-label="Close the filter"
          @click=${() => t.close()}
        >
          <svg class="menu-entry-icon" viewBox="0 0 24 24" aria-hidden="true">
            <path d="${Qa}"></path>
          </svg></button
        >${r.desc}
        </div>
      </div>
    </div>`;
}, to = { reason: null }, no = { reason: "Choose where to plug it in first" }, ro = { reason: "Choose where to move it first" }, io = { reason: "Tick or untick something first" }, ao = { reason: "Tick a row first" }, oo = { reason: "Fix the marked rows first" }, so = Xe, co = "Creates the Wall Sockets now; adds the links to the batch, which take effect on Commit", lo = {
	blank: "The Wall Socket needs a name.",
	existing: "A Wall Socket with this name already exists. Choose a different name.",
	new: "Another new Wall Socket has this name. Choose a different name."
}, uo = (e, t, n, r) => {
	let { dialog: i } = t, a = J(i.choices, e);
	if (a.kind === "none") return "";
	let o = Pa(a), s = Pa({ kind: "new" }), c = `wall-batch-${e.coId}`, l = Ia(e, t.state, t.areaNames), u = (t, n) => v`
      <label class="choice-row">
        <input
          type="radio"
          name=${c}
          value=${t}
          .checked=${t === o}
          ?disabled=${i.saving}
          @change=${() => r.chooseRow(e.coId, t)}
        />
        ${n}
      </label>
    `, d = a.kind === "new";
	return v`
      <div class="wall-batch-options ${O("small-text")}">
      ${u(s, "New")}
      <input
        type="text"
        class="from-names-name"
        data-id=${e.coId}
        aria-label="New Wall Socket name for ${e.label}"
        .value=${q(e, i.edits)}
        ?readonly=${!d || i.saving}
        tabindex=${d && !i.saving ? 0 : -1}
        @input=${(t) => r.editName(e.coId, t.target.value)}
      />${n === null ? "" : v`<p class="from-names-note from-names-error ${D("dialog-field-note")} ${O("error-text")}"><svg class="from-names-error-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${so}"></path></svg><span>${lo[n]}</span></p>`}
      ${l.map((e) => u(e.value, e.label))}
      </div>
    `;
}, fo = (e, t, n, r) => {
	if (!e) return v`<dialog class="wall-batch-dialog ${A("modal-dialog-box")}" @close=${() => t.close()}></dialog>`;
	let { dialog: i, state: a, rows: o } = e, s = i.choices, c = Ra(o, s, i.edits), l = za(o, s, i.edits, a.uos), u = Va(o, s), d = ja(o, s, i.filter);
	return v`
      <dialog
        class="wall-batch-dialog ${A("modal-dialog-box")}"
        @close=${() => t.close()}
        @cancel=${(e) => t.cancel(e)}
      >
        <div class="dialog-body">
          ${k("Wall Sockets for Smart Devices", r)}
          ${o.length === 0 ? v`<p class=${O("supporting-text")}>Every Smart Device already has a Wall Socket.</p>` : v`
                <div class="from-names-toolbar">
                  ${n.renderDialogFilter(i.filter, i.saving, (e) => t.setFilter(e))}
                  <button
                    class="plain-btn"
                    ?disabled=${i.saving}
                    @click=${() => t.setChoices(Ba(d, s, i.edits, a.uos))}
                  >
                    Tick all
                  </button>
                  <button class="plain-btn" ?disabled=${i.saving} @click=${() => t.setChoices({})}>
                    Untick all
                  </button>
                  <span class="from-names-counts ${D("dialog-field-note")}">
                    ${u} of ${o.length} ticked${d.length < o.length ? v` · ${d.length} shown` : ""}${l.size > 0 ? v` · <span class="from-names-error-count ${O("error-text")}">${l.size} duplicate${l.size === 1 ? "" : "s"}</span>` : ""}${c.size > 0 ? v` · <span class="from-names-error-count ${O("error-text")}">${c.size} need${c.size === 1 ? "s" : ""} a name</span>` : ""}
                  </span>
                </div>
                <div class="from-names-scroll">
                  <table class="from-names-table">
                    <thead>
                      <tr>
                        <th class=${D("column-heading")}>Room</th>
                        <th class=${D("column-heading")}></th>
                        <th class=${D("column-heading")}>Smart Device</th>
                        <th class="from-names-col-name ${D("column-heading")}">Wall Socket</th>
                      </tr>
                    </thead>
                    <tbody>
                      ${Ma(d).map((n) => n.rows.map((r, a) => v`
                            <tr>
                              ${a === 0 ? v`<td class="from-names-integration" rowspan=${n.rows.length}>
                                    <span class=${O("emphasis")}>${Oa(n.areaName)}</span>
                                  </td>` : ""}
                              <td>
                                <label class="choice-row">
                                  <input
                                    type="checkbox"
                                    aria-label="Give ${r.label} a Wall Socket"
                                    .checked=${J(s, r).kind !== "none"}
                                    ?disabled=${i.saving}
                                    @change=${() => t.toggleRow(r.coId)}
                                  />
                                </label>
                              </td>
                              <td class="from-names-ha-name ${D("dialog-field-note")}">${ka(r)}</td>
                              <td class="from-names-col-name">
                                ${uo(r, e, c.has(r.coId) ? "blank" : l.get(r.coId) ?? null, t)}
                              </td>
                            </tr>
                          `))}
                    </tbody>
                  </table>
                  ${d.length === 0 ? v`<p class=${O("supporting-text")}>${Fn}</p>` : ""}
                </div>
              `}
          ${i.failures.map((e) => v`<p class="error ${O("error-text")}">${e.label}: ${e.message}</p>`)}
        </div>
        <div class="dialog-actions">
          <button ?disabled=${i.saving} @click=${() => t.close()}>Cancel</button>
          ${n.renderStagingButton({
		label: `Apply ${u}`,
		tip: co,
		className: "go",
		disabled: i.saving ? to : u === 0 ? ao : c.size > 0 || l.size > 0 ? oo : !1,
		onClick: () => t.apply()
	})}
        </div>
      </dialog>
    `;
}, po = (e) => {
	let t = e.replace(/'+/g, "-").normalize("NFKD").replace(/⁄/g, "/").replace(/\p{M}+/gu, "").toLowerCase().replace(/'+/g, "").replace(/(?<=\d),(?=\d)/g, "").replace(/[^-a-z0-9]+/g, "-").replace(/-{2,}/g, "-").replace(/^-|-$/g, "").replace(/-/g, "_");
	return t === "" ? "unknown" : t;
}, mo = (e, t = null) => po(`ob ${e}${t ? ` ${t}` : ""}`), ho = (e) => po(e), go = (e) => e === null || e.trim() === "", _o = (e, t) => {
	let n = new Map(e.cos.map((e) => [e.co_id, e])), r = /* @__PURE__ */ new Map();
	for (let t of e.appliances) {
		let e = mo(t.name, t.type);
		r.has(e) || r.set(e, t.name);
	}
	let i = [];
	for (let r of e.co_sockets) {
		if (r.occupant_device_id !== null) continue;
		let e = t[r.co_socket_id]?.name ?? null;
		if (e === null || go(e)) continue;
		let a = n.get(r.co_id);
		a && i.push({
			sortKey: I(a),
			position: r.position,
			row: {
				coSocketId: r.co_socket_id,
				coId: r.co_id,
				integrationDomain: t[r.co_socket_id]?.integration_domain ?? null,
				friendlyName: t[r.co_socket_id]?.friendly_name ?? null,
				defaultName: e
			}
		});
	}
	let a = (e) => e.integrationDomain === null ? "￿" : e.integrationDomain;
	return i.sort((e, t) => a(e.row).localeCompare(a(t.row)) || F(e.sortKey, t.sortKey) || e.row.coId.localeCompare(t.row.coId) || e.position - t.position), {
		rows: i.map((e) => e.row),
		existing: r
	};
}, vo = () => /* @__PURE__ */ new Set(), yo = (e, t) => t[e.coSocketId] ?? e.defaultName, bo = (e) => j(e.integrationDomain), xo = (e) => j(e.friendlyName), So = (e) => e.trim() === "" ? null : `….${ho(e)}_…`, Co = (e, t) => {
	let n = yo(e, t);
	return [
		bo(e),
		n,
		So(n),
		xo(e)
	];
}, wo = (e, t, n, r) => e.filter((e) => t.has(e.coSocketId) || Rn(r, Co(e, n))), To = (e, t, n, r) => {
	let i = /* @__PURE__ */ new Map(), a = /* @__PURE__ */ new Map(), o = (e) => e.friendlyName ?? e.defaultName;
	for (let s of e) {
		let e = n.has(s.coSocketId), c = yo(s, r), l = null, u = "duplicate";
		if (!go(c)) {
			let e = t.get(mo(c));
			e !== void 0 && (l = `Clashes with the Appliance “${e}”. Choose a different name.`);
		}
		if (l === null && e && go(c) && (l = "The Appliance needs a name.", u = "blank"), l === null && e) {
			let e = mo(c), t = a.get(e);
			t ? l = `Clashes with “${yo(t, r)}” (Socket “${o(t)}”). Choose a different name.` : a.set(e, s);
		}
		l !== null && i.set(s.coSocketId, {
			text: l,
			kind: u,
			blocking: e
		});
	}
	return i;
}, Eo = (e) => Array.from(e.values()).filter((e) => e.blocking).length, Do = (e, t) => Array.from(e.values()).filter((e) => e.blocking && e.kind === t).length, Oo = (e, t, n) => {
	let r = new Set(e.map((e) => e.coSocketId)), i = To(e, t, r, n);
	return new Set(Array.from(r).filter((e) => !i.has(e)));
}, ko = (e, t, n) => e.filter((e) => t.has(e.coSocketId)).map((e) => ({
	row: e,
	name: yo(e, n).trim()
})), Ao = (e) => {
	let t = [];
	for (let n of e) {
		let e = t[t.length - 1];
		e && e.integrationDomain === n.integrationDomain ? e.rows.push(n) : t.push({
			integrationDomain: n.integrationDomain,
			rows: [n]
		});
	}
	return t;
}, jo = (e) => e.candidates.some((e) => e.disabledBy === null), Mo = (e) => {
	let t = new Set(e.candidates.map((e) => e.action));
	return t.size === 0 || t.size === 1 && t.has("appliance_into_socket") ? "Appliance" : t.size === 1 && t.has("co_into_co_socket") ? "Smart Device" : "Plug in";
}, No = (e) => Array.from(new Set(e.candidates.filter((e) => e.disabledBy === null).map((e) => e.uoName).filter((e) => e !== null))).sort(F), Po = (e, t) => {
	let n = /* @__PURE__ */ new Map();
	for (let r of e.candidates) r.disabledBy === null && r.coId !== null && r.coAlias !== null && (t === null || r.uoName === t) && (n.has(r.coId) || n.set(r.coId, {
		alias: r.coAlias,
		place: r.groupContext ?? r.context
	}));
	let r = /* @__PURE__ */ new Map();
	for (let { alias: e } of n.values()) r.set(e, (r.get(e) ?? 0) + 1);
	return Array.from(n, ([e, { alias: t, place: n }]) => ({
		coId: e,
		alias: t,
		text: (r.get(t) ?? 0) > 1 ? `${t} (${j(n)})` : t
	})).sort((e, t) => F(e.alias, t.alias) || F(e.text, t.text) || e.coId.localeCompare(t.coId)).map(({ coId: e, text: t }) => ({
		coId: e,
		text: t
	}));
}, Fo = "Already powering:", Io = "Powering:", Lo = (e) => `${e}:`, Ro = (e) => `${e.label}${e.disabledBy ? ` — ${e.disabledBy.kind === "current" ? "current" : e.disabledBy.name}` : e.note === null ? "" : " —"}`, zo = (e) => e.context === null ? null : `(${e.context})`, Bo = (e) => e.groupContext === null ? null : `(${e.groupContext})`, Vo = (e) => [
	e.groupLabel === null ? "" : Lo(e.groupLabel),
	Bo(e) ?? "",
	Ro(e),
	zo(e) ?? "",
	e.note === null ? "" : `${Fo} ${e.note}`
], Ho = (e, t) => e.trim() === "" || Rn(e, t()), Uo = { kind: "available" }, Wo = (e) => e.kind === "co" ? `co:${e.coId}` : e.kind, Go = (e) => e === "all" ? { kind: "all" } : e.startsWith("co:") ? {
	kind: "co",
	coId: e.slice(3)
} : Uo, Ko = {
	room: null,
	co: null
}, qo = (e) => e.disabledBy === null || e.groupLabel !== null, Jo = (e, t) => e === null ? qo(t) : e.kind === "all" || e.kind === "available" && t.disabledBy === null || e.kind === "co" && (t.coId === null || t.coId === e.coId), Yo = (e) => e.candidates.filter(qo), Xo = (e) => e.view === "picker" ? new Set(e.selectedId === null ? [] : [e.selectedId]) : /* @__PURE__ */ new Set([...e.rows.filter((t) => !e.selectedIds.has(t.deviceId)).map((e) => e.deviceId), ...e.selectedCandidateIds]), Zo = (e) => ({
	...e,
	pinned: Xo(e)
}), Qo = (e, t, n) => e.pinned.has(t) || n.has(t), $o = (e, t, n) => Qo(e, t.id, Xo(e)) || (n.room === null || t.uoName === n.room) && Jo(n.co, t) && Ho(e.filter, () => Vo(t)), es = (e, t) => e.candidates.filter((n) => $o(e, n, t)), ts = (e) => new Set(e.map((e) => e.kind)).size > 1, ns = (e, t) => t ? `(${e === "co" ? "Smart Device" : "Appliance"})` : null, rs = (e, t) => [
	e.label,
	ns(e.kind, t) ?? "",
	e.powering.length === 0 ? "" : `${Io} ${e.powering.join(", ")}`
], is = (e, t) => [e.label, ns(e.kind, t) ?? ""], as = (e) => {
	let t = ts(e.rows), n = Xo(e);
	return e.rows.filter((r) => Qo(e, r.deviceId, n) || Ho(e.filter, () => rs(r, t)));
}, os = (e) => {
	let t = ts(e.candidates), n = Xo(e);
	return e.candidates.filter((r) => Qo(e, r.deviceId, n) || Ho(e.filter, () => is(r, t)));
}, ss = {
	appliance_into_socket: {
		wsType: "outlet_binder/create_plugged_into",
		plugField: "appliance_id",
		socketField: "co_socket_id"
	},
	co_into_uo: {
		wsType: "outlet_binder/assign_co_to_uo",
		plugField: "co_id",
		socketField: "uo_id"
	},
	co_into_co_socket: {
		wsType: "outlet_binder/assign_co_to_co_socket",
		plugField: "co_id",
		socketField: "co_socket_id"
	}
}, cs = (e, t) => {
	let n = ss[t.action], r = e.kind === "co_socket";
	return {
		type: n.wsType,
		[n.plugField]: r ? t.id : e.subjectId,
		[n.socketField]: r ? e.subjectId : t.id
	};
}, ls = {
	co: {
		plug: "outlet_binder/assign_co_to_uo",
		unplug: "outlet_binder/unassign_co_from_uo",
		deviceField: "co_id"
	},
	appliance: {
		plug: "outlet_binder/assign_appliance_to_uo",
		unplug: "outlet_binder/unassign_appliance_from_uo",
		deviceField: "appliance_id"
	}
}, us = (e, t) => {
	let n = ls[t.kind];
	return {
		type: n.plug,
		[n.deviceField]: t.deviceId,
		uo_id: e
	};
}, ds = (e) => {
	let t = ls[e.kind];
	return {
		type: t.unplug,
		[t.deviceField]: e.deviceId
	};
}, fs = (e, t) => {
	let n = e.cosById.get(t), r = n === void 0 ? null : R(n);
	return r?.kind === "uo" ? e.uoNames.get(r.id) ?? r.id : null;
}, ps = (e, t) => {
	let n = e.cosById.get(t);
	if (n === void 0) return null;
	let r = R(n);
	switch (r.kind) {
		case "uo": return e.uoNames.get(r.id) ?? r.id;
		case "co_socket": {
			let t = e.socketsById.get(r.id);
			return t === void 0 ? null : B(e, t);
		}
		case "nowhere": return null;
	}
}, ms = (e, t) => {
	let n = ps(e, t), r = e.cosById.get(t);
	if (n === null || r === void 0) return null;
	let i = R(r);
	return {
		text: n,
		target: i.kind === "uo" ? pr(e, i.id) : i.kind === "co_socket" ? hr(e, i.id) : null
	};
}, hs = (e, t) => {
	let n = e.cosById.get(t);
	if (n === void 0) return null;
	let r = R(n);
	return r.kind === "co_socket" ? e.socketsById.get(r.id)?.co_id ?? null : null;
}, gs = (e, t) => e.coNames.get(t) ?? t, _s = (e, t) => {
	let n = ps(e, t.co_id);
	return `${B(e, t)}${n === null ? "" : ` (${n})`}`;
}, vs = (e) => [...e].sort((e, t) => F(e.label, t.label)), ys = (e) => {
	let t = e.findIndex((e) => e.disabledBy?.kind === "current");
	if (t === -1) return e;
	let n = e[t].groupKey;
	if (n === null) return e;
	let r = t;
	for (; r > 0 && e[r - 1].groupKey === n;) --r;
	let i = t;
	for (; i < e.length - 1 && e[i + 1].groupKey === n;) i += 1;
	let a = e.slice(r, i + 1), o = [...e.slice(0, r), ...e.slice(i + 1)];
	return [...a, ...o];
}, bs = (e, t) => ys(Array.from(e.socketsById.values()).filter((e) => !t.excludeCoIds.has(e.co_id)).map((t) => ({
	sock: t,
	prefixLabel: gs(e, t.co_id)
})).sort((e, t) => F(e.prefixLabel, t.prefixLabel) || e.sock.co_id.localeCompare(t.sock.co_id) || F(e.sock.alias, t.sock.alias)).map(({ sock: n }) => {
	let r = Qn(n, e), i = n.co_socket_id === t.currentSocketId ? { kind: "current" } : r === null ? null : {
		kind: "occupied",
		name: j(r.name)
	}, a = (e.socketsByCo.get(n.co_id) ?? []).length > 1, o = ps(e, n.co_id), s = gs(e, n.co_id);
	return {
		id: n.co_socket_id,
		label: a ? n.alias : s,
		fullLabel: _s(e, n),
		context: a ? null : o,
		disabledBy: i,
		groupLabel: a ? s : null,
		groupContext: a ? o : null,
		groupKey: a ? n.co_id : null,
		note: null,
		action: t.action,
		uoName: fs(e, n.co_id),
		coAlias: gs(e, n.co_id),
		coId: n.co_id
	};
})), xs = (e, t) => {
	let n = z(e), r = n.kind === "co_socket" ? n.id : null, i = bs(t, {
		currentSocketId: r,
		excludeCoIds: /* @__PURE__ */ new Set(),
		action: "appliance_into_socket"
	}), a = r === null ? void 0 : t.socketsById.get(r), o = n.kind === "uo" ? t.uoNames.get(n.id) ?? n.id : null;
	return {
		view: "picker",
		kind: "appliance",
		subjectId: e.appliance_id,
		subjectLabel: e.name,
		linked: n.kind !== "nowhere",
		currentLabel: a ? {
			text: _s(t, a),
			target: U(t, a.co_id)
		} : o !== null && n.kind === "uo" ? {
			text: o,
			target: pr(t, n.id)
		} : null,
		currentHaDevice: a?.co_id ?? null,
		subjectHaDevice: null,
		powering: [],
		contextLabel: null,
		candidates: i,
		selectedId: null,
		filter: "",
		pinned: /* @__PURE__ */ new Set(),
		unlink: n.kind === "nowhere" ? null : {
			wsType: n.kind === "uo" ? "outlet_binder/unassign_appliance_from_uo" : "outlet_binder/unplug_plugged_into",
			payload: { appliance_id: e.appliance_id },
			label: `Unplug ${e.name}`
		},
		saving: !1,
		error: null
	};
}, Ss = (e, t) => (e.socketsByCo.get(t) ?? []).flatMap((t) => {
	let n = Qn(t, e);
	return n === null ? [] : [{
		text: j(n.name),
		target: gr(t, e)
	}];
}), Cs = (e, t) => Ss(e, t).map((e) => e.text), ws = (e, t) => {
	let n = /* @__PURE__ */ new Set();
	for (let r of e.cosById.values()) {
		let i = [r.co_id], a = r;
		for (; a !== void 0;) {
			let r = R(a);
			if (r.kind !== "co_socket") break;
			let o = e.socketsById.get(r.id)?.co_id;
			if (o === void 0 || i.includes(o)) break;
			if (o === t) {
				for (let e of i) n.add(e);
				break;
			}
			i.push(o), a = e.cosById.get(o);
		}
	}
	return n;
}, Ts = (e) => {
	switch (e) {
		case "co_into_uo": return "outlets";
		case "co_into_co_socket":
		case "appliance_into_socket": return "sockets";
	}
}, Es = (e) => ({
	outlets: e.filter((e) => Ts(e.action) === "outlets"),
	sockets: e.filter((e) => Ts(e.action) === "sockets")
}), Ds = (e, t) => {
	let n = R(e), r = n.kind === "uo" ? n.id : null, i = n.kind === "co_socket" ? n.id : null, a = vs(Array.from(t.uosById.values()).filter((e) => e.uo_id !== r).map((e) => {
		let n = t.cosByUo.get(e.uo_id) ?? [], r = n.length === 0 ? null : n.map((e) => e.alias).join(", ");
		return {
			id: e.uo_id,
			label: e.name,
			fullLabel: e.name,
			context: null,
			disabledBy: null,
			groupLabel: null,
			groupContext: null,
			groupKey: null,
			note: r,
			action: "co_into_uo",
			uoName: null,
			coAlias: null,
			coId: null
		};
	})), o = e.has_plug ? [...a, ...bs(t, {
		currentSocketId: i,
		excludeCoIds: /* @__PURE__ */ new Set([e.co_id, ...ws(t, e.co_id)]),
		action: "co_into_co_socket"
	}).map((e) => ({
		...e,
		uoName: null
	}))] : [], s = r === null ? void 0 : t.uosById.get(r), c = i === null ? void 0 : t.socketsById.get(i);
	return {
		view: "picker",
		kind: "co",
		subjectId: e.co_id,
		subjectLabel: e.alias,
		linked: n.kind !== "nowhere",
		currentLabel: s ? {
			text: s.name,
			target: {
				kind: "uo",
				entity: s
			}
		} : c ? {
			text: _s(t, c),
			target: U(t, c.co_id)
		} : null,
		currentHaDevice: s ? null : c?.co_id ?? null,
		subjectHaDevice: e.co_id,
		powering: Ss(t, e.co_id),
		contextLabel: null,
		candidates: o,
		selectedId: null,
		filter: "",
		pinned: /* @__PURE__ */ new Set(),
		unlink: n.kind === "uo" ? {
			wsType: "outlet_binder/unassign_co_from_uo",
			payload: { co_id: e.co_id },
			label: `Unplug from ${s?.name ?? j(null)}`
		} : n.kind === "co_socket" ? {
			wsType: "outlet_binder/unassign_co_from_co_socket",
			payload: { co_id: e.co_id },
			label: `Unplug from ${j(c ? t.coNames.get(c.co_id) ?? null : null)}`
		} : null,
		saving: !1,
		error: null
	};
}, Os = (e, t) => {
	let n = Qn(e, t);
	if (n !== null) {
		let r = j(n.name);
		return {
			view: "picker",
			kind: "co_socket",
			subjectId: e.co_socket_id,
			subjectLabel: B(t, e),
			linked: !0,
			currentLabel: {
				text: r,
				target: gr(e, t)
			},
			currentHaDevice: e.plugged_into_appliance_id === null ? n.id : null,
			subjectHaDevice: null,
			powering: [],
			contextLabel: null,
			candidates: [],
			selectedId: null,
			filter: "",
			pinned: /* @__PURE__ */ new Set(),
			unlink: e.plugged_into_appliance_id === null ? {
				wsType: "outlet_binder/unassign_co_from_co_socket",
				payload: { co_id: n.id },
				label: `Unplug ${r}`
			} : {
				wsType: "outlet_binder/unplug_plugged_into",
				payload: { appliance_id: n.id },
				label: `Unplug ${r}`
			},
			saving: !1,
			error: null
		};
	}
	let r = (e, t) => (n) => ({
		id: n.id,
		label: n.label,
		fullLabel: n.label,
		context: null,
		disabledBy: null,
		groupLabel: t,
		groupContext: null,
		groupKey: t,
		note: null,
		action: e,
		uoName: null,
		coAlias: null,
		coId: null
	}), i = vs(Array.from(t.appliancesById.values()).filter((e) => z(e).kind === "nowhere").map((e) => ({
		id: e.appliance_id,
		label: e.name
	}))), a = vs(Array.from(t.cosById.values()).filter((n) => n.has_plug && n.co_id !== e.co_id && R(n).kind === "nowhere" && !ws(t, n.co_id).has(e.co_id)).map((e) => ({
		id: e.co_id,
		label: e.alias
	}))), o = i.length > 0 && a.length > 0, s = [...i.map(r("appliance_into_socket", o ? "Appliances" : null)), ...a.map(r("co_into_co_socket", o ? "Smart Devices" : null))];
	return {
		view: "picker",
		kind: "co_socket",
		subjectId: e.co_socket_id,
		subjectLabel: B(t, e),
		linked: !1,
		currentLabel: null,
		currentHaDevice: null,
		subjectHaDevice: e.co_id,
		powering: [],
		contextLabel: {
			placeName: ms(t, e.co_id),
			placeHaDevice: hs(t, e.co_id)
		},
		candidates: s,
		selectedId: s.length === 1 ? s[0].id : null,
		filter: "",
		pinned: /* @__PURE__ */ new Set(),
		unlink: null,
		saving: !1,
		error: null
	};
}, ks = (e, t) => {
	let n = (e, t) => (e.kind === t.kind ? 0 : e.kind === "co" ? -1 : 1) || F(e.label, t.label), r = [...(t.cosByUo.get(e.uo_id) ?? []).map((e) => ({
		deviceId: e.co_id,
		kind: "co",
		label: e.alias,
		powering: Cs(t, e.co_id)
	})), ...(t.appliancesByUo.get(e.uo_id) ?? []).map((e) => ({
		deviceId: e.appliance_id,
		kind: "appliance",
		label: e.name,
		powering: []
	}))].sort(n), i = [...Array.from(t.cosById.values()).filter((e) => e.has_plug && R(e).kind === "nowhere").map((e) => ({
		deviceId: e.co_id,
		kind: "co",
		label: e.alias
	})), ...Array.from(t.appliancesById.values()).filter((e) => z(e).kind === "nowhere").map((e) => ({
		deviceId: e.appliance_id,
		kind: "appliance",
		label: e.name
	}))].sort(n);
	return {
		view: "multi",
		kind: "uo",
		subjectId: e.uo_id,
		subjectLabel: e.name,
		rows: r,
		selectedIds: new Set(r.map((e) => e.deviceId)),
		failures: [],
		candidates: i,
		selectedCandidateIds: /* @__PURE__ */ new Set(),
		candidateFailures: [],
		filter: "",
		pinned: /* @__PURE__ */ new Set(),
		saving: !1,
		error: null
	};
}, As = (e) => {
	switch (e.kind) {
		case "appliance": return z(e.entity).kind !== "nowhere";
		case "co": return R(e.entity).kind !== "nowhere";
		case "co_socket": return e.entity.occupant_device_id !== null;
		case "uo": return Zn(e.entity);
	}
}, js = (e) => {
	switch (e.kind) {
		case "co": return R(e.entity).kind === "co_socket" ? "hosted" : "unplug";
		case "co_socket": return e.entity.plugged_into_appliance_id === null ? "hosting" : "unplug";
		case "appliance":
		case "uo": return "unplug";
	}
}, Ms = (e, t) => {
	switch (e.kind) {
		case "appliance": return e.entity.name;
		case "co": return e.entity.alias;
		case "co_socket": return B(t, e.entity);
	}
}, Ns = {
	appliance: {
		one: "Appliance",
		many: "Appliances"
	},
	co: {
		one: "Smart Device",
		many: "Smart Devices"
	}
}, Ps = {
	uo: {
		one: "Wall Socket",
		many: "Wall Sockets"
	},
	co_socket: {
		one: "Smart Device socket",
		many: "Smart Device sockets"
	}
}, Fs = (e, t, n) => {
	let [r] = e;
	if (e.length === 1 && r !== void 0) return {
		label: "Available",
		value: t(r)
	};
	if (n === void 0) return {
		label: "Available",
		value: String(e.length)
	};
	let { kindOf: i, nouns: a } = n, o = /* @__PURE__ */ new Map();
	for (let t of e) {
		let e = i(t);
		o.set(e, (o.get(e) ?? 0) + 1);
	}
	let s = Object.keys(a).filter((e) => o.has(e)), c = String(e.length);
	return s.length < 2 ? {
		label: "Available",
		value: c
	} : {
		label: "Available",
		value: c,
		items: s.map((e) => {
			let t = o.get(e) ?? 0;
			return `${t} ${t === 1 ? a[e].one : a[e].many}`;
		})
	};
}, Is = (e, t) => {
	switch (e.kind) {
		case "uo": return N(t.uoNames, e.id);
		case "co_socket": {
			let n = t.socketsById.get(e.id);
			return n === void 0 ? j(null) : _s(t, n);
		}
		case "nowhere": return j(null);
	}
}, Ls = (e, t) => e.kind === "co_socket" ? er(t, e.entity) : Ms(e, t), Rs = {
	appliance: "Nothing to plug into",
	co: "Add a Wall Socket first",
	co_socket: "Nothing to plug in"
}, zs = (e, t) => {
	let n = ks(e.entity, t), r = n.candidates.length, i = n.rows.length, a = As(e), o = r === 0 && i === 0, s = e.entity.name, c = Fs(n.candidates, (e) => e.label, {
		kindOf: (e) => e.kind,
		nouns: Ns
	}), l = {
		label: "Plugged in",
		value: n.rows.map((e) => e.label).join(", ")
	}, u = o ? {
		action: "No devices to plug in or unplug",
		blocked: !0
	} : r > 0 ? i > 0 ? {
		action: `Plug in, or unplug ${i}`,
		attrs: [c, l]
	} : {
		action: "Plug in",
		attrs: [c]
	} : {
		action: "Unplug",
		attrs: [l]
	};
	return {
		linked: a,
		disabled: o,
		iconKind: a ? "unplug" : "socket",
		hover: K("uo", s, u),
		ariaLabel: Ws("uo", r > 0 || o, s)
	};
}, Bs = (e, t) => ({
	linked: !1,
	disabled: !0,
	iconKind: "plug",
	hover: K("co", e, {
		action: "Fixed in place",
		blocked: !0
	}),
	ariaLabel: Ws("co", !0, t)
}), Vs = {
	co_socket: (e, t) => {
		let n = Os(e.entity, t).candidates;
		return {
			count: n.length,
			attr: Fs(n, (e) => e.fullLabel, {
				kindOf: (e) => e.action === "co_into_co_socket" ? "co" : "appliance",
				nouns: Ns
			})
		};
	},
	appliance: (e, t) => {
		let n = xs(e.entity, t).candidates.filter((e) => e.disabledBy === null);
		return {
			count: n.length,
			attr: Fs(n, (e) => e.fullLabel)
		};
	},
	co: (e, t) => {
		let n = Ds(e.entity, t).candidates.filter((e) => e.disabledBy === null);
		return {
			count: n.length,
			attr: Fs(n, (e) => e.fullLabel, {
				kindOf: (e) => e.action === "co_into_co_socket" ? "co_socket" : "uo",
				nouns: Ps
			})
		};
	}
}, Hs = (e, t) => {
	if (As(e)) return null;
	let n = Vs[e.kind];
	return n(e, t);
}, Us = (e, t) => {
	if (e.kind === "uo") return zs(e, t);
	let n = As(e), r = Ms(e, t), i = Ls(e, t);
	if (e.kind === "co" && !e.entity.has_plug) return Bs(r, i);
	let a = n ? js(e) : e.kind === "co_socket" ? "socket" : "plug", o = Hs(e, t), s = n && (e.kind === "appliance" || e.kind === "co") && jo(e.kind === "appliance" ? xs(e.entity, t) : Ds(e.entity, t)), c = o?.count === 0, l = o === null ? {
		action: s ? "Unplug / Move" : "Unplug",
		attrs: [e.kind === "co_socket" ? {
			label: "Plugged in",
			value: Os(e.entity, t).currentLabel?.text ?? j(null)
		} : {
			label: "Plugged into",
			value: Is(e.kind === "appliance" ? z(e.entity) : R(e.entity), t)
		}]
	} : o.count === 0 ? {
		action: Rs[e.kind],
		blocked: !0
	} : {
		action: "Plug in",
		attrs: [o.attr]
	};
	return {
		linked: n,
		disabled: c,
		iconKind: a,
		hover: K(e.kind, r, l),
		ariaLabel: Ws(e.kind, !n, i)
	};
}, Ws = (e, t, n) => e === "co_socket" || e === "uo" ? `${t ? "Plug into" : "Unplug from"} ${n}` : `${t ? "Plug in" : "Unplug"} ${n}`, Gs = (e) => e.saving || e.selectedIds.size === e.rows.length && e.selectedCandidateIds.size === 0, Ks = () => {
	let e = !1;
	return {
		next: () => e,
		recordSuccess: () => {
			e = !0;
		}
	};
}, qs = (e, t, n) => {
	let { failures: r, candidateFailures: i, filter: a } = n, o = ks(e, t), s = new Set(r.map((e) => e.deviceId)), c = new Set(i.map((e) => e.deviceId));
	return Zo({
		...o,
		selectedIds: new Set(o.rows.map((e) => e.deviceId).filter((e) => !s.has(e))),
		failures: r,
		selectedCandidateIds: new Set(o.candidates.map((e) => e.deviceId).filter((e) => c.has(e))),
		candidateFailures: i,
		filter: a
	});
}, Js = async (e, t) => {
	let n = Ks(), r = [];
	for (let i of e) {
		if ("failed" in i) {
			r.push({
				item: i.item,
				error: i.failed
			});
			continue;
		}
		try {
			await t({
				...i.message,
				continue_group: n.next()
			}), n.recordSuccess();
		} catch (e) {
			r.push({
				item: i.item,
				error: e
			});
		}
	}
	return r;
}, Ys = (e) => e.linked ? jo(e) ? "Unplug / Move:" : `${W[e.kind]}:` : e.kind === "co_socket" ? "Plug in to socket:" : "Plug in:", Xs = (e, t) => e.unlink ? "Move to…" : t ? "Into a socket in:" : e.kind === "co_socket" ? `${Mo(e)}:` : "Into:", Zs = (e) => e.saving ? "busy" : e.selectedId === null ? e.unlink ? "choose_move" : "choose_plug_in" : null, Qs = (e, t) => {
	let n = e.kind === "appliance", r = n ? No(e) : [], i = n || e.kind === "co" ? Po(e, n ? t.room : null) : [], a = r.length > 0 || i.length > 0, o = n && a, s = Yo(e).length;
	return {
		titleLabel: Ys(e),
		roomOptions: r,
		coOptions: i,
		hasFilters: a,
		showsDropdownsInBar: o,
		visible: es(e, a ? {
			room: n ? t.room : null,
			co: t.co
		} : Ko),
		offeredCount: s,
		hasFilterBar: o || s > 1,
		currentWord: s > 0 ? "Plugged into:" : "Currently:",
		loneCandidate: s === 1 && e.kind === "co_socket",
		listHeading: Xs(e, o),
		socketsHeading: i.length === 0 ? "title" : "co_dropdown",
		primary: s > 0 ? {
			label: e.unlink ? "Move" : "Plug in",
			disabled: Zs(e)
		} : null,
		unplugBusy: e.saving
	};
}, $s = Xe, ec = "Creates the Appliances now; adds the plug-ins to the batch, which take effect on Commit", tc = (e, t, n, r, i) => {
	let a = t.ticked.has(e.coSocketId), o = a && !t.saving, s = yo(e, t.edits), c = So(s);
	return v`
      <tr class="${n?.blocking ? "from-names-blocked" : ""} ${n ? "from-names-has-note" : ""}">
        ${r ? v`<td class="from-names-integration" rowspan=${r.span}>
              <span class=${O("emphasis")}>${bo(e)}</span>
            </td>` : ""}
        <td>
          <label class="choice-row">
            <input
              type="checkbox"
              aria-label="Create Appliance"
              .checked=${a}
              ?disabled=${t.saving}
              @change=${() => i.toggleRow(e.coSocketId)}
            />
          </label>
        </td>
        <td class="from-names-col-name">
          <input
            type="text"
            class="from-names-name"
            data-id=${e.coSocketId}
            aria-label="Appliance name"
            .value=${s}
            ?readonly=${!o}
            tabindex=${o ? 0 : -1}
            @input=${(t) => i.editName(e.coSocketId, t.target.value)}
          />
          ${c === null ? "" : v`<p class="from-names-slug ${D("dialog-metadata")}">${c}</p>`}
        </td>
        <td class="from-names-ha-name ${D("dialog-field-note")}">${xo(e)}</td>
      </tr>
      ${n ? v`<tr class="from-names-note-row ${n.blocking ? "from-names-blocked" : ""}">
            <td></td>
            <td colspan="2">
              <p class="from-names-note ${D("dialog-field-note")} ${n.blocking ? `from-names-error ${O("error-text")}` : ""}">${n.blocking ? v`<svg class="from-names-error-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${$s}"></path></svg>` : ""}<span>${n.text}</span></p>
            </td>
          </tr>` : ""}
    `;
}, nc = (e, t, n, r) => {
	if (!e) return v`<dialog class="from-names-dialog ${A("modal-dialog-box")}" @close=${() => t.close()}></dialog>`;
	let i = To(e.rows, e.existing, e.ticked, e.edits), a = Eo(i), o = Do(i, "duplicate"), s = Do(i, "blank"), c = ko(e.rows, e.ticked, e.edits).length, l = wo(e.rows, e.ticked, e.edits, e.filter), u = Ao(l);
	return v`
      <dialog
        class="from-names-dialog ${A("modal-dialog-box")}"
        @close=${() => t.close()}
        @cancel=${(e) => t.cancel(e)}
      >
        <div class="dialog-body">
          ${k("Appliances from Socket names", r)}
          ${e.loading ? v`<p class=${O("supporting-text")}>Loading the Socket names…</p>` : e.loadError ? v`<p class="error ${O("error-text")}">${e.loadError}</p>` : e.rows.length === 0 ? v`<p class=${O("supporting-text")}>No empty Socket has a name of its own in Home Assistant to make an Appliance from.</p>` : v`
                <div class="from-names-toolbar">
                  ${n.renderDialogFilter(e.filter, e.saving, (e) => t.setFilter(e))}
                  <button
                    class="plain-btn"
                    ?disabled=${e.saving}
                    @click=${() => t.setTicks(Oo(l, e.existing, e.edits))}
                  >
                    Tick all
                  </button>
                  <button class="plain-btn" ?disabled=${e.saving} @click=${() => t.setTicks(/* @__PURE__ */ new Set())}>
                    Untick all
                  </button>
                  <span class="from-names-counts ${D("dialog-field-note")}">
                    ${c} of ${e.rows.length} ticked${l.length < e.rows.length ? v` · ${l.length} shown` : ""}${o > 0 ? v` · <span class="from-names-error-count ${O("error-text")}">${o} duplicate${o === 1 ? "" : "s"}</span>` : ""}${s > 0 ? v` · <span class="from-names-error-count ${O("error-text")}">${s} need${s === 1 ? "s" : ""} a name</span>` : ""}
                  </span>
                </div>
                <div class="from-names-scroll">
                  <table class="from-names-table">
                    <thead>
                      <tr>
                        <th class=${D("column-heading")}>Integration</th>
                        <th class=${D("column-heading")}></th>
                        <th class="from-names-col-name ${D("column-heading")}">Create Appliance <br /><span class="from-names-th-sub ${D("dialog-field-note")}">(based on HA Entity Name)</span></th>
                        <th class=${D("column-heading")}>HA Entity Name <br /><span class="from-names-th-sub ${D("dialog-field-note")}">(from Smart Socket integration)</span></th>
                      </tr>
                    </thead>
                    <tbody>
                      ${u.map((n) => {
		let r = n.rows.length + n.rows.filter((e) => i.has(e.coSocketId)).length;
		return n.rows.map((a, o) => tc(a, e, i.get(a.coSocketId) ?? null, o === 0 ? {
			group: n,
			span: r
		} : null, t));
	})}
                    </tbody>
                  </table>
                  ${l.length === 0 ? v`<p class=${O("supporting-text")}>${Fn}</p>` : ""}
                </div>
              `}
          ${e.failures.map((e) => v`<p class="error ${O("error-text")}">${e.label}: ${e.message}</p>`)}
        </div>
        <div class="dialog-actions">
          <button ?disabled=${e.saving} @click=${() => t.close()}>Cancel</button>
          ${n.renderStagingButton({
		label: `Apply ${c}`,
		tip: ec,
		className: "go",
		disabled: e.saving || e.loading ? to : c === 0 ? ao : a > 0 && oo,
		onClick: () => t.apply()
	})}
        </div>
      </dialog>
    `;
};
//#endregion
//#region src/outlet-binder-panel/settings-view.ts
function rc(e, t, n) {
	return v`
    <dialog class="settings-dialog ${A("modal-dialog-box")}" @close=${() => t()}>
      <div class="dialog-body">
        ${k("Settings", n)}
        ${e}
      </div>
      <div class="dialog-actions">
        <button @click=${() => t()}>Close</button>
      </div>
    </dialog>
  `;
}
//#endregion
//#region src/outlet-binder-panel/ha-items-state.ts
var ic = (e) => e.entity_id.split(".")[0] ?? "", ac = (e) => {
	let t = e.find((e) => e.on_off) ?? null, n = /* @__PURE__ */ new Map();
	for (let r of e) {
		if (r === t) continue;
		let e = ic(r), i = n.get(e);
		i === void 0 ? n.set(e, [r]) : i.push(r);
	}
	return {
		onOff: t,
		groups: Array.from(n, ([e, t]) => ({
			label: e.replaceAll("_", " "),
			items: t
		}))
	};
};
//#endregion
//#region src/outlet-binder-panel/ha-items-view.ts
function oc(e, t, n) {
	return v`
    <dialog
      class="ha-items-dialog ${A("modal-dialog-box")}"
      @close=${() => t()}
    >
      ${e === null ? b : v`<div class="ha-items-head">
              ${k(v`<span class=${O("ob-element-name")}>Entities:</span>
                  ${e.name}`, n)}
              <p class="ha-items-prompt ${O("ob-element-name")}">
                Open in Home Assistant:
              </p>
            </div>
            <div class="ha-items-scroll">
              ${e.layout.onOff === null ? b : e.renderItem(e.layout.onOff)}
            ${e.layout.groups.map((t) => v`<div class="ha-items-group">
                <p
                  class="ha-items-group-heading ${O("supporting-text", "italic-text")}"
                >
                  ${t.label}
                </p>
                ${t.items.map(e.renderItem)}
              </div>`)}
          </div>`}
      <div class="dialog-actions">
        <button autofocus @click=${() => t()}>Close</button>
      </div>
    </dialog>
  `;
}
//#endregion
//#region src/outlet-binder-panel/discovered-view.ts
function sc(e, t, n, r) {
	return v`
    <dialog class="discovered-dialog ${A("modal-dialog-box")}" @close=${() => t()}>
      ${e ? v`
            <div class="dialog-body">
              ${k(e.heading, r)}
              ${e.entries.map((e) => v`
                  <p class=${O("supporting-text")}><span class=${O("emphasis")}>${n.renderMention(e.title)}</span></p>
                  ${n.renderAttrList(e.fields)}
                `)}
            </div>
            <div class="dialog-actions">
              <button @click=${() => t()}>Close</button>
            </div>
          ` : ""}
    </dialog>
  `;
}
//#endregion
//#region src/outlet-binder-panel/from-names-state.ts
var cc = () => ({
	loading: !0,
	loadError: null,
	names: {},
	rows: [],
	existing: /* @__PURE__ */ new Map(),
	ticked: /* @__PURE__ */ new Set(),
	edits: {},
	filter: "",
	saving: !1,
	error: null,
	failures: []
}), lc = (e, t, n) => {
	if (!e) return null;
	let { rows: r, existing: i } = _o(e, t);
	return {
		loading: !1,
		loadError: null,
		names: t,
		rows: r,
		existing: i,
		ticked: vo(),
		edits: n,
		filter: "",
		saving: !1,
		error: null,
		failures: []
	};
}, uc = (e, t) => ({
	...e,
	loading: !1,
	loadError: t
}), dc = (e, t) => ({
	...e,
	ticked: t
}), fc = (e, t) => ({
	...e,
	filter: t
}), pc = (e, t, n) => ({
	...e,
	edits: {
		...e.edits,
		[t]: n
	}
}), mc = (e, t) => {
	let n = new Set(e), r = !n.has(t);
	return r ? n.add(t) : n.delete(t), {
		ticked: n,
		ticking: r
	};
}, hc = (e) => ({
	...e,
	saving: !0,
	error: null,
	failures: []
}), gc = (e, t, n, r) => ({
	...e,
	ticked: new Set(e.rows.filter((e) => t.has(e.coSocketId)).map((e) => e.coSocketId)),
	filter: n,
	failures: r
}), _c = (e, t) => Math.max((e.get(t.co_id) ?? []).length, 1), vc = (e, t) => {
	switch (t.kind) {
		case "live": return _c(e, t.co);
		case "copy": return t.sockets.length;
		case "direct": return 1;
	}
}, yc = (e, t) => t.rows.reduce((t, n) => t + vc(e, n) + +!!n.gapBefore, 0), bc = (e) => ({
	socketTotal: e.full.socketTotal + e.partial.socketTotal + e.orphan.socketTotal,
	socketInUse: e.full.socketInUse + e.partial.socketInUse + e.orphan.socketInUse
}), xc = (e, t, n, r) => e.filtering ? !e.blocks.has(r) : t.has(n), Sc = (e, t, n) => {
	let r = [], i = !1;
	for (let a of e) {
		let e = t[a];
		if (e.length === 0) continue;
		let o = !n.filtering || e.some((e, t) => n.blocks.has(ga(a, t)));
		r.push({
			section: a,
			blocks: e,
			headed: o,
			spacerBefore: o && i
		}), o && (i = !0);
	}
	return r;
}, Cc = () => {
	let e = 0;
	return () => {
		let t = e % 2 == 1;
		return e += 1, t ? "row-shade" : "";
	};
}, wc = (e) => e.cursor_seq > 0, Tc = (e) => e.cursor_seq < e.entry_count, Ec = (e, t) => `${e} ${t}${e === 1 ? "" : "s"}`, Dc = {
	create_plugged_into: {
		verb: "Plug",
		ids: [["appliance", "appliance_id"], ["co_socket", "co_socket_id"]]
	},
	unplug_plugged_into: {
		verb: "Unplug",
		ids: [["appliance", "appliance_id"]]
	},
	assign_co_to_uo: {
		verb: "Assign",
		ids: [["co", "co_id"], ["uo", "uo_id"]]
	},
	assign_appliance_to_uo: {
		verb: "Assign",
		ids: [["appliance", "appliance_id"], ["uo", "uo_id"]]
	},
	unassign_appliance_from_uo: {
		verb: "Unassign",
		ids: [["appliance", "appliance_id"]]
	},
	unassign_co_from_uo: {
		verb: "Unassign",
		ids: [["co", "co_id"]]
	},
	assign_co_to_co_socket: {
		verb: "Plug",
		ids: [["co", "co_id"], ["co_socket", "co_socket_id"]]
	},
	unassign_co_from_co_socket: {
		verb: "Unassign",
		ids: [["co", "co_id"]]
	}
}, Oc = (e) => Object.hasOwn(Dc, e), kc = (e) => {
	let t = Oc(e.command) ? Dc[e.command] : void 0;
	return {
		command: e.command,
		verb: t?.verb ?? e.command,
		ids: (t?.ids ?? []).map(([t, n]) => ({
			role: t,
			id: e.payload[n]
		}))
	};
}, Ac = (e) => {
	let t = [];
	for (let n of e) {
		let e = kc(n), r = t.at(-1);
		r && r.group_seq === n.group_seq ? r.entries.push(e) : t.push({
			group_seq: n.group_seq,
			entries: [e]
		});
	}
	return t.map(({ entries: e }) => ({ entries: e }));
}, jc = (e) => Ac(e.commit_entries), Mc = (e) => Ac(e.flush_entries), Nc = (e) => Ac(e.commit_entries).reverse(), Pc = (e) => Ac(e.flush_entries.slice(e.commit_entries.length)), Fc = (e) => {
	let t = wc(e), n = Tc(e), r = e.entry_count > 0, i = e.failed_entry !== null, a = e.undo_group_count, o = e.redo_group_count, s = e.undo_group_count + e.redo_group_count;
	return {
		undo: {
			disabled: !t,
			count: a,
			title: t ? `Undo the last staged change (${a} pending)` : "Nothing to undo"
		},
		redo: {
			disabled: !n,
			count: o,
			title: n ? `Redo the next staged change (${o} pending)` : "Nothing to redo"
		},
		commit: {
			disabled: !t || i,
			count: a,
			title: i ? "Undo past the failed change, or flush, before committing" : t ? `Apply the staged changes (${a} pending)` : "Nothing to commit"
		},
		flush: {
			disabled: !r,
			count: s,
			title: r ? `Discard every staged change (${s} pending)` : "Nothing staged"
		}
	};
}, Ic = (e, t, n) => {
	if (t === null) return;
	let r = e.get(t) ?? [];
	r.push(n), e.set(t, r);
}, Lc = (e) => {
	let t = Xn(e);
	return t.kind === "nowhere" ? null : t;
}, Rc = (e, t) => e === null || t === null ? e === t : e.kind === t.kind && e.id === t.id, zc = (e, t, n) => {
	t !== null && Ic(t.kind === "uo" ? e.uo : e.coSocket, t.id, n);
}, Bc = (e, t) => {
	let n = {
		appliance: /* @__PURE__ */ new Map(),
		co: /* @__PURE__ */ new Map(),
		coSocket: /* @__PURE__ */ new Map(),
		uo: /* @__PURE__ */ new Map()
	};
	if (t === null) return n;
	for (let r of e.appliances) {
		let e = t.appliances[r.appliance_id];
		if (e === void 0) continue;
		let i = Lc(e), a = Lc(r);
		if (Rc(i, a)) continue;
		let o = {
			kind: "appliance",
			subjectId: r.appliance_id,
			from: i,
			to: a
		};
		Ic(n.appliance, r.appliance_id, o), zc(n, o.from, o), zc(n, o.to, o);
	}
	for (let r of e.cos) {
		let e = t.cos[r.co_id];
		if (e === void 0) continue;
		let i = Lc(e), a = Lc(r);
		if (Rc(i, a)) continue;
		let o = {
			kind: "co",
			subjectId: r.co_id,
			from: i,
			to: a
		};
		Ic(n.co, r.co_id, o), zc(n, o.from, o), zc(n, o.to, o);
	}
	return n;
}, Vc = (e, t, n) => t ? n.coSocket.get(e)?.find((t) => t.from?.kind === "co_socket" && t.from.id === e) ?? null : null, Hc = (e, t, n) => t === null ? `Plug ${e} into ${j(n)}` : n === null ? `Unplug ${e} from ${t}` : `Move ${e} from ${t} to ${n}`;
//#endregion
//#region \0@oxc-project+runtime@0.147.0/helpers/esm/decorate.js
function X(e, t, n, r) {
	var i = arguments.length, a = i < 3 ? t : r === null ? r = Object.getOwnPropertyDescriptor(t, n) : r, o;
	if (typeof Reflect == "object" && typeof Reflect.decorate == "function") a = Reflect.decorate(e, t, n, r);
	else for (var s = e.length - 1; s >= 0; s--) (o = e[s]) && (a = (i < 3 ? o(a) : i > 3 ? o(t, n, a) : o(t, n)) || a);
	return i > 3 && a && Object.defineProperty(t, n, a), a;
}
//#endregion
//#region src/outlet-binder-panel/panel.ts
var Uc = {
	busy: to,
	choose_move: ro,
	choose_plug_in: no
}, Z = `unbound ${O("small-text", "disabled-text")}`, Wc = ut, Gc = Ct, Kc = lt, qc = dt, Jc = St, Yc = Ze, Xc = ct, Zc = Tt, Qc = Qe, $c = $e, el = at, tl = ot, nl = nt, rl = ft, il = Ot, al = Dt, ol = Ot, sl = Et, cl = kt, ll = "Adds this change to the batch; it takes effect on Commit", ul = {
	tools: wt,
	appliance: Wc,
	filter: el,
	export: it
}, dl = 6, fl = (e) => v`<tr class="section-spacer"><td colspan="${e}"></td></tr>`, pl = (e) => v`<tbody class="${e ? "collapsed" : ""}" ?inert=${e}>
    ${fl(dl)}
  </tbody>`, ml = [
	"full",
	"partial",
	"orphan"
], hl = (e) => {
	let t = getComputedStyle(e);
	if (t.boxSizing === "border-box") return {
		height: 0,
		width: 0
	};
	let n = (e) => Number.parseFloat(e) || 0;
	return {
		height: n(t.paddingTop) + n(t.paddingBottom) + n(t.borderTopWidth) + n(t.borderBottomWidth),
		width: n(t.paddingLeft) + n(t.paddingRight) + n(t.borderLeftWidth) + n(t.borderRightWidth)
	};
}, gl = "none", _l = (e) => Wr(e) ? e : null, Q = (e, t) => {
	let n = document.createElement("div");
	return n.className = e, n.textContent = t, n;
}, vl = (e, t) => {
	let n = document.createElementNS("http://www.w3.org/2000/svg", "svg");
	n.setAttribute("class", e), n.setAttribute("viewBox", "0 0 24 24"), n.setAttribute("aria-hidden", "true");
	let r = document.createElementNS("http://www.w3.org/2000/svg", "path");
	return r.setAttribute("d", t), n.appendChild(r), n;
}, yl = {
	dirty: "Save or cancel your changes first",
	saving: "Wait for the save to finish first"
}, bl = (e) => {
	switch (e.kind) {
		case "uo": return e.entity.name;
		case "co": return e.entity.alias;
		case "appliance": return e.entity.name;
	}
}, xl = {
	_editing: "edit-dialog",
	_editingSocket: "socket-edit-dialog"
}, $ = class extends He {
	constructor(...e) {
		super(...e), this._state = null, this._editSession = null, this._debugMode = !1, this._build = null, this._error = null, this._loading = !1, this._socketRegion = "uk", this._haItems = {}, this._mode = "batch", this._themeOverride = ni(), this._collapsedSections = hi(), this._collapsedCardBandGroups = xi(), this._layoutTier = "wide", this._activeTab = wi(), this._editing = null, this._editingSocket = null, this._linking = null, this._linkRoomFilter = null, this._linkCoFilter = Uo, this._heldDialogs = /* @__PURE__ */ new Set(), this._dialogMin = /* @__PURE__ */ new WeakMap(), this._creating = null, this._deleting = null, this._flushConfirm = null, this._commitConfirm = null, this._settingsOpen = !1, this._menuOpen = !1, this._mainFilter = "", this._filterOpen = !1, this._filterPos = null, this._filterDrag = null, this._fromNames = null, this._exporting = null, this._wallBatch = null, this._discovered = null, this._areas = wa(null, null), this._areasSource = null, this._fetched = !1, this._tipShown = !1, this._tipSeq = 0, this._tipHost = null, this._tipTimer = null, this._pointerPos = null, this._lastPointerType = null, this._lastInput = null, this._onWindowResize = () => {
			this._hideTip(), this._keepMainFilterOnScreen();
		}, this._onDocumentClick = (e) => {
			e.composedPath().some((e) => e instanceof Element && e.classList.contains("menu-wrap")) || this._closeMenu();
		}, this._resizeObserver = null, this._dialogObserver = null, this._newCoIds = /* @__PURE__ */ new Set(), this._helpersCache = null, this._renderHaItem = (e) => {
			let t = e.vendor?.toUpperCase();
			return v`<button
      class="ha-item ${bn()}"
      aria-label=${`Open ${e.name}${t === void 0 ? "" : ` [${t}]`} in Home Assistant`}
      @click=${() => {
				let t = jn(e.entity_id, this._topLocation());
				this._setHaItemsOpen(!1), this._openInHomeAssistant(t);
			}}
    >
      <span class=${e.on_off ? O("emphasis") : ""}
        >${e.name}${e.vendor === null ? "" : v` <span class=${O("supporting-text")}
                >[${t}]</span
              >`}</span
      >${this._renderHaLogo()}
    </button>`;
		};
	}
	static {
		this.styles = [Cn, Sn];
	}
	firstUpdated() {
		let e = this.renderRoot, t = (t, n, r = !1) => e.addEventListener(t, n, r);
		t("pointerover", (e) => this._tipEvent("pointerover", e)), t("pointerout", (e) => this._tipEvent("pointerout", e)), t("focusin", (e) => this._tipEvent("focusin", e)), t("focusout", (e) => this._tipEvent("focusout", e)), t("click", (e) => this._tipEvent("click", e)), t("pointermove", (e) => this._trackPointer(e)), t("pointerdown", (e) => {
			this._lastPointerType = e.pointerType, this._lastInput = "pointer";
		}), t("keydown", (e) => {
			this._lastInput = "keyboard", e.key === "Escape" && (this._tipEvent("escape", e), this._menuOpen && (this._closeMenu(), this._menuBtnEl?.focus()));
		}), t("scroll", () => this._hideTip(), !0);
	}
	connectedCallback() {
		super.connectedCallback(), window.addEventListener("resize", this._onWindowResize), this._dialogObserver = new ResizeObserver((e) => {
			for (let t of e) t.target instanceof HTMLDialogElement && this._holdDialogSize(t.target);
		}), this._resizeObserver = new ResizeObserver((e) => {
			let t = e[0]?.contentRect.width;
			if (t === void 0) return;
			let n = nr(t);
			n !== this._layoutTier && (this._layoutTier = n);
		}), this._resizeObserver.observe(this);
	}
	disconnectedCallback() {
		window.removeEventListener("resize", this._onWindowResize), document.removeEventListener("click", this._onDocumentClick), this._resizeObserver?.disconnect(), this._resizeObserver = null, this._dialogObserver?.disconnect(), this._dialogObserver = null, this._heldDialogs.clear(), this._hideTip(), super.disconnectedCallback();
	}
	_trackPointer(e) {
		e.pointerType !== "touch" && (this._pointerPos = {
			left: e.clientX,
			top: e.clientY
		});
	}
	_tipEvent(e, t) {
		e === "pointerover" && this._trackPointer(t);
		let n = e === "escape" ? null : t.target?.closest("[data-tip]") ?? null;
		switch (zr({
			event: e,
			host: n ? n.getAttribute("data-tip") : null,
			pointerType: this._lastPointerType,
			lastInput: this._lastInput
		})) {
			case "ignore": return;
			case "hide":
				this._hideTip();
				return;
			case "show":
				n && this._showTip(n);
				return;
			case "toggle":
				n && (this._tipHost === n ? this._hideTip() : this._showTip(n));
				return;
			case "showDelayed":
				n && (this._hideTip(), this._tipTimer = setTimeout(() => {
					this._tipTimer = null, this._showTip(n, this._pointerPos);
				}, 300));
				return;
		}
	}
	_showTip(e, t = null) {
		let n = this._popoverEl, r = e.getAttribute("aria-describedby"), i = r ? this.renderRoot.querySelector(`#${r}`) : null, a = i?.textContent;
		if (!n || !i || !a) return;
		this._hideTip(), this._fillPopover(n, i, a), n.showPopover(), this._tipShown = !0;
		let { left: o, top: s } = Rr(e.getBoundingClientRect(), n.getBoundingClientRect(), {
			width: window.innerWidth,
			height: window.innerHeight
		}, t);
		n.style.left = `${o}px`, n.style.top = `${s}px`, this._tipHost = e;
	}
	_fillPopover(e, t, n) {
		let r = t.getAttribute("data-hover");
		if (r !== null) {
			this._fillHoverPopover(e, Qr(n, _l(r), t.getAttribute("data-blocked") === "true"));
			return;
		}
		let { title: i, body: a } = Vr(n), o = [];
		if (i !== "" && o.push(Q(`tip-title ${D("hover-title")}`, i)), a !== "") {
			let e = Hr(a), t = document.createElement("div");
			t.className = "tip-body", t.style.setProperty("--tip-marker", `${Math.max(0, ...e.map((e) => e.marker.length))}ch`);
			for (let n of e) {
				let e = document.createElement("div");
				e.className = `tip-line ${n.kind}`, n.kind !== "plain" && e.appendChild(Q(`tip-marker ${D("hover-data")}`, n.marker)), e.appendChild(Q(`tip-text-cell ${D("hover-data")}`, n.text)), t.appendChild(e);
			}
			o.push(t);
		}
		e.replaceChildren(...o);
	}
	_fillHoverPopover(e, t) {
		let n = Q(`tip-title ${D("hover-title")}`, "");
		t.icon !== null && n.appendChild(vl("tip-icon", this._hoverIconPath(t.icon))), n.appendChild(document.createTextNode(t.title));
		let r = [n];
		if (t.action !== "") {
			let e = Q(`${t.blocked ? "tip-action blocked" : "tip-action"} ${D("hover-action")}`, "");
			t.blocked && e.appendChild(vl("tip-no-entry", Kc)), e.appendChild(document.createTextNode(t.action)), t.blocked && e.appendChild(vl("tip-no-entry end", Kc)), r.push(e);
		}
		if (t.attrs.length > 0) {
			let e = Q("tip-attrs", "");
			for (let n of t.attrs) {
				e.append(Q(`tip-attr-label ${D("hover-prompt")}`, n.label === "" ? "" : `${n.label}:`), Q(`tip-attr-value ${D("hover-data")}`, n.value));
				for (let t of n.items ?? []) e.appendChild(Q(`tip-attr-item ${D("hover-data")}`, `- ${t}`));
			}
			r.push(e);
		}
		e.replaceChildren(...r);
	}
	_hoverIconPath(e) {
		switch (e) {
			case "appliance": return Wc;
			case "co": return Gc;
			case "uo": return xa[this._socketRegion];
		}
	}
	_hideTip() {
		this._tipTimer !== null && (clearTimeout(this._tipTimer), this._tipTimer = null), this._tipShown && this._popoverEl?.hidePopover(), this._tipShown = !1, this._tipHost = null;
	}
	willUpdate(e) {
		e.has("hass") && this._refreshAreas(), e.has("hass") && this.hass && !this._fetched && (this._fetched = !0, this._loading = !0, this.hass.callWS({ type: "outlet_binder/discover_cos" }).catch((e) => {
			console.warn("outlet_binder/discover_cos failed", e);
		}).then((e) => this.hass.callWS({ type: "outlet_binder/get_state" }).then((t) => ({
			created: e?.created ?? [],
			state: t
		}))).then(({ created: e, state: t }) => {
			let { newIds: n, nextSeen: r } = oi(t.cos, ii(), Date.now());
			ai(r), this._newCoIds = n, this._state = t, this._editSession = t.edit_session, this._debugMode = t.debug_mode, this._build = t.build, this._socketRegion = t.socket_region, this._haItems = t.ha_items, this._mode = t.mode, this._discovered = na(e, t, this._registries()) ? e : null, this._error = null;
		}).catch((e) => {
			this._error = Nn("Failed to load state", e);
		}).finally(() => {
			this._loading = !1;
		}));
	}
	updated() {
		this._tipHost && !this._tipHost.isConnected && this._hideTip(), L(this._dialogEl, this._editing !== null), L(this._socketDialogEl, this._editingSocket !== null), L(this._linkDialogEl, this._linking !== null), L(this._createDialogEl, this._creating !== null), L(this._deleteDialogEl, this._deleting !== null), L(this._flushDialogEl, this._flushConfirm !== null), L(this._commitDialogEl, this._commitConfirm !== null), L(this._settingsDialogEl, this._settingsOpen), L(this._haItemsDialogEl, this._haItemsOpen()), L(this._fromNamesDialogEl, this._fromNames !== null), L(this._exportDialogEl, this._exporting !== null), L(this._wallBatchDialogEl, this._wallBatch !== null), L(this._discoveredDialogEl, this._discovered !== null), this._holdDialogSizes(), this._themeOverride === "system" ? this.removeAttribute("data-theme") : this.setAttribute("data-theme", this._themeOverride);
	}
	_holdDialogSizes() {
		for (let e of Array.from(this._heldDialogs)) (!e.open || !e.isConnected) && this._releaseDialog(e);
		for (let e of Array.from(this.shadowRoot?.querySelectorAll("dialog") ?? [])) !e.open || this._heldDialogs.has(e) || (this._heldDialogs.add(e), this._dialogObserver?.observe(e));
	}
	_releaseDialog(e) {
		this._dialogObserver?.unobserve(e), this._heldDialogs.delete(e), e.style.minHeight = "", e.style.minWidth = "", this._dialogMin.delete(e);
	}
	_holdDialogSize(e) {
		if (!e.open) return;
		let { height: t, width: n } = e.getBoundingClientRect(), r = this._dialogMin.get(e) ?? {
			height: 0,
			width: 0
		};
		if (t <= r.height + 1 && n <= r.width + 1) return;
		let i = {
			height: Math.max(t, r.height),
			width: Math.max(n, r.width)
		};
		this._dialogMin.set(e, i);
		let a = hl(e);
		e.style.minHeight = `min(${i.height - a.height}px, calc(100vh - 6em))`, e.style.minWidth = `min(${i.width - a.width}px, calc(100vw - 6em))`;
	}
	async _refresh() {
		if (this.hass) try {
			let e = await this.hass.callWS({ type: "outlet_binder/get_state" }), { newIds: t, nextSeen: n } = oi(e.cos, ii(), Date.now());
			ai(n), this._newCoIds = t, this._state = e, this._editSession = e.edit_session, this._debugMode = e.debug_mode, this._build = e.build, this._socketRegion = e.socket_region, this._haItems = e.ha_items, this._mode = e.mode, this._error = null;
		} catch (e) {
			this._error = Nn("Failed to refresh after save", e);
		}
	}
	_openEdit(e) {
		if (!this._state) return;
		let t = V(this._state);
		switch (e.kind) {
			case "uo":
				this._editing = ur("uo", e.entity.uo_id, Or(e.entity));
				return;
			case "appliance": {
				let n = z(e.entity), r = n.kind === "co_socket" ? n.id : null;
				this._editing = ur("appliance", e.entity.appliance_id, Mr(e.entity, t, r === null ? null : void 0)), r !== null && this._loadApplianceHaName(e.entity.appliance_id, r);
				return;
			}
			case "co":
				this._editing = ur("co", e.entity.co_id, Pr(e.entity, t, this._areas.names));
				return;
		}
	}
	_openSocketEdit(e) {
		this._state && (this._editingSocket = ur("co_socket", e.co_socket_id, Fr(e, V(this._state))));
	}
	async _followLink(e) {
		this._hideTip(), this._linking = null, this._editingSocket = null, this._editing = null, this._discovered = null, await this.updateComplete;
		let t = this._helpers();
		if (!t) return;
		let n = e.kind === "uo" ? pr(t, e.entity.uo_id) : e.kind === "co" ? U(t, e.entity.co_id) : mr(t, e.entity.appliance_id);
		n && this._openEdit(n);
	}
	_closeEdit(e) {
		this[e] = null;
	}
	_haItemsOpen() {
		return this._editing?.kind === "appliance" && this._editing.haItemsOpen;
	}
	_setHaItemsOpen(e) {
		this._editing && this._editing.haItemsOpen !== e && (this._editing = {
			...this._editing,
			haItemsOpen: e
		});
	}
	_updateDraftField(e, t, n) {
		let r = this[e];
		r && (this[e] = {
			...r,
			draft: {
				...r.draft,
				[t]: n
			}
		});
	}
	_isEditValid(e) {
		return Sr(e);
	}
	async _saveEdit(e) {
		let t = this[e];
		if (!t || !this.hass) return;
		let n = Cr(t);
		this[e] = {
			...t,
			saving: !0,
			error: null
		};
		try {
			await this.hass.callWS(n), this._closeEdit(e), await this._refresh();
		} catch (t) {
			this[e] = fr(this[e], t);
		}
	}
	_openDeleteConfirm(e) {
		let t, n, r;
		switch (e.kind) {
			case "uo":
				t = "uo", n = e.entity.uo_id, r = `Delete ${W.uo} "${e.entity.name}"?`;
				break;
			case "appliance":
				t = "appliance", n = e.entity.appliance_id, r = `Delete ${W.appliance} "${e.entity.name}"?`;
				break;
			case "co":
				t = "co", n = e.entity.co_id, r = `Reset "${e.entity.alias}" to its newly-discovered defaults? All edits to this Smart Device and its Sockets will be lost, and it will reappear on the next panel load.`;
				break;
			case "co_socket": return;
		}
		this._deleting = {
			kind: t,
			id: n,
			message: r,
			saving: !1,
			error: null
		};
	}
	_closeDeleteConfirm() {
		this._deleting = null;
	}
	async _confirmDelete() {
		let e = this._deleting;
		if (!e || !this.hass) return;
		let t = Tr[e.kind];
		this._deleting = {
			...e,
			saving: !0,
			error: null
		};
		try {
			await this.hass.callWS({
				type: t.wsType,
				[t.idField]: e.id
			}), this._closeDeleteConfirm(), await this._refresh();
		} catch (e) {
			this._deleting = fr(this._deleting, e);
		}
	}
	_openSettings() {
		this._settingsOpen = !0;
	}
	_toggleMenu() {
		this._menuOpen ? this._closeMenu() : this._openMenu();
	}
	_openMenu() {
		this._menuOpen = !0, document.addEventListener("click", this._onDocumentClick);
	}
	_closeMenu() {
		this._menuOpen = !1, document.removeEventListener("click", this._onDocumentClick);
	}
	_chooseMenuAction(e) {
		switch (this._closeMenu(), e) {
			case "show_filter":
				this._showMainFilter();
				return;
			case "create_appliances_from_socket_names":
				this._openFromNames();
				return;
			case "assign_uos_to_smart_devices":
				this._openWallBatch();
				return;
			case "export_state":
				this._exporting = Mt();
				return;
			default: throw Error(`Unhandled menu action: ${String(e)}`);
		}
	}
	async _loadApplianceHaName(e, t) {
		let n = null;
		try {
			n = (await this.hass?.callWS({ type: "outlet_binder/get_socket_ha_names" }))?.[t]?.friendly_name ?? null;
		} catch (e) {
			console.warn("outlet_binder/get_socket_ha_names failed", e);
		}
		let r = this._editing;
		!r || r.kind !== "appliance" || r.id !== e || (this._editing = {
			...r,
			readonlyFields: r.readonlyFields.map((e) => e[0] === "Socket's HA name" ? Ar(n) : e)
		});
	}
	_closeSettings() {
		this._settingsOpen = !1;
	}
	async _openFromNames() {
		if (!this.hass) return;
		let e = cc();
		this._fromNames = e;
		try {
			await this._refresh();
			let t = await this.hass.callWS({ type: "outlet_binder/get_socket_ha_names" });
			if (this._fromNames !== e) return;
			this._fromNames = lc(this._state, t, {}) ?? uc(e, "Couldn't read the Socket names");
		} catch (t) {
			if (this._fromNames !== e) return;
			this._fromNames = uc(e, Nn("Couldn't read the Socket names", t));
		}
	}
	_closeExport() {
		this._exporting = null;
	}
	_updateExport(e) {
		this._exporting = Nt(this._exporting, e);
	}
	async _runExport() {
		let e = this._exporting;
		if (!(!e || e.saving || !this.hass)) {
			this._exporting = {
				...e,
				saving: !0,
				error: null
			};
			try {
				let t = await this.hass.callWS(Pt(e));
				if (!this._exporting) return;
				It(t, e.format), this._closeExport();
			} catch (e) {
				this._updateExport({
					saving: !1,
					error: Nn("Couldn't export the state", e)
				});
			}
		}
	}
	_closeFromNames() {
		this._fromNames = null;
	}
	_setFromNamesTicks(e) {
		this._fromNames &&= dc(this._fromNames, e);
	}
	_setFromNamesFilter(e) {
		this._fromNames &&= fc(this._fromNames, e);
	}
	_editFromNamesName(e, t) {
		this._fromNames &&= pc(this._fromNames, e, t);
	}
	_toggleFromNamesRow(e) {
		if (!this._fromNames) return;
		let { ticked: t, ticking: n } = mc(this._fromNames.ticked, e);
		this._setFromNamesTicks(t), n && this.updateComplete.then(() => {
			let t = this.shadowRoot?.querySelector(`input.from-names-name[data-id="${e}"]`);
			t?.focus(), t?.select();
		});
	}
	async _applyFromNames() {
		let e = this._fromNames;
		if (!e || !this.hass) return;
		let t = ko(e.rows, e.ticked, e.edits), n = To(e.rows, e.existing, e.ticked, e.edits);
		if (t.length === 0 || Eo(n) > 0) return;
		this._fromNames = hc(e);
		let r = new Set((this._state?.appliances ?? []).map((e) => e.appliance_id)), i = [], a = /* @__PURE__ */ new Set(), o = ({ row: e }, t) => {
			a.add(e.coSocketId), i.push({
				label: e.friendlyName ?? e.defaultName,
				message: P(t)
			});
		};
		for (let e of t) try {
			await this.hass.callWS({
				type: "outlet_binder/create_appliance",
				name: e.name
			});
		} catch (t) {
			o(e, t);
		}
		t.length > a.size && await this._refresh();
		let s = new Map((this._state?.appliances ?? []).filter((e) => !r.has(e.appliance_id)).map((e) => [e.name, e.appliance_id])), c = this.hass, l = t.flatMap((e) => {
			if (a.has(e.row.coSocketId)) return [];
			let t = s.get(e.name);
			return t === void 0 ? [{
				item: e,
				failed: /* @__PURE__ */ Error("The new Appliance was not found after creating it")
			}] : [{
				item: e,
				message: {
					type: "outlet_binder/create_plugged_into",
					appliance_id: t,
					co_socket_id: e.row.coSocketId
				}
			}];
		});
		for (let { item: e, error: t } of await Js(l, (e) => c.callWS(e))) o(e, t);
		if (await this._refresh(), i.length === 0) {
			this._closeFromNames();
			return;
		}
		let u = lc(this._state, e.names, e.edits);
		if (!u) {
			this._closeFromNames();
			return;
		}
		this._fromNames = gc(u, a, e.filter, i);
	}
	_wallBatchRows() {
		return this._state ? Da(this._state, (e) => Un(this.hass?.devices, e).area_id, this._areas.names) : [];
	}
	_openWallBatch() {
		this._wallBatch = Ua();
	}
	_closeWallBatch() {
		this._wallBatch = null;
	}
	_toggleWallBatchRow(e) {
		let t = this._wallBatch;
		t && this._setWallBatchChoice(e, Ga(t, e));
	}
	_chooseWallBatch(e, t) {
		this._setWallBatchChoice(e, Fa(t));
	}
	_setWallBatchChoice(e, t) {
		let n = this._wallBatch;
		n && (this._wallBatch = Wa(n, e, t), t.kind === "new" && this.updateComplete.then(() => {
			let t = this.shadowRoot?.querySelector(`input.from-names-name[data-id="${e}"]`);
			t?.focus(), t?.select();
		}));
	}
	_setWallBatchChoices(e) {
		this._wallBatch &&= Ka(this._wallBatch, e);
	}
	_setWallBatchFilter(e) {
		this._wallBatch &&= qa(this._wallBatch, e);
	}
	_editWallBatchName(e, t) {
		let n = this._wallBatch;
		n && (this._wallBatch = Ja(n, e, t));
	}
	async _applyWallBatch() {
		let e = this._wallBatch;
		if (!e || !this.hass || !this._state) return;
		let t = this._wallBatchRows(), n = Ha(t, e.choices, e.edits);
		if (n.assigns.length === 0 || Ra(t, e.choices, e.edits).size > 0 || za(t, e.choices, e.edits, this._state.uos).size > 0) return;
		this._wallBatch = Ya(e);
		let r = [], i = /* @__PURE__ */ new Map();
		for (let e of n.creates) {
			let t = new Set((this._state?.uos ?? []).map((e) => e.uo_id));
			try {
				await this.hass.callWS({
					type: "outlet_binder/create_uo",
					name: e.name,
					ha_area_id: e.areaId
				}), await this._refresh();
				let n = (this._state?.uos ?? []).filter((e) => !t.has(e.uo_id)), [r] = n;
				if (n.length !== 1 || !r) throw Error("The new Wall Socket was not found after creating it");
				i.set(e.coId, r.uo_id);
			} catch (t) {
				r.push({
					label: e.label,
					message: P(t)
				});
			}
		}
		let a = this.hass, o = n.assigns.flatMap((e) => {
			let t = e.target.kind === "existing" ? e.target.uoId : i.get(e.coId);
			return t === void 0 ? [] : [{
				item: e.label,
				message: {
					type: "outlet_binder/assign_co_to_uo",
					co_id: e.coId,
					uo_id: t
				}
			}];
		});
		for (let { item: e, error: t } of await Js(o, (e) => a.callWS(e))) r.push({
			label: e,
			message: P(t)
		});
		if (await this._refresh(), r.length === 0) {
			this._closeWallBatch();
			return;
		}
		this._wallBatch = Xa(e, r);
	}
	_openCreate(e) {
		this._creating = {
			kind: e,
			draft: { ...Dr[e] },
			saving: !1,
			error: null
		};
	}
	_refreshAreas() {
		let e = this.hass?.areas, t = this.hass?.floors;
		(this._areasSource?.areas !== e || this._areasSource?.floors !== t) && (this._areasSource = {
			areas: e,
			floors: t
		}, this._areas = wa(e, t));
	}
	_registries() {
		return {
			devices: this.hass?.devices,
			areas: this.hass?.areas,
			floors: this.hass?.floors
		};
	}
	_coDevice(e) {
		return Un(this.hass?.devices, e.co_id);
	}
	_closeCreate() {
		this._creating = null;
	}
	_updateCreateDraftField(e, t) {
		this._creating &&= {
			...this._creating,
			draft: {
				...this._creating.draft,
				[e]: t
			}
		};
	}
	_isCreateValid(e) {
		let t = Er[e.kind].requiredField;
		return e.draft[t].trim() !== "";
	}
	async _saveCreate() {
		let e = this._creating;
		if (!e || !this.hass) return;
		let t = Er[e.kind], n = (e) => e.trim() === "" ? null : e, r = { type: t.wsType };
		for (let [i, a] of Object.entries(e.draft)) r[i] = i === t.requiredField ? a : n(a);
		this._creating = {
			...e,
			saving: !0,
			error: null
		};
		try {
			await this.hass.callWS(r), this._closeCreate(), await this._refresh();
		} catch (e) {
			this._creating = fr(this._creating, e);
		}
	}
	_maybeNewBadge(e) {
		return this._newCoIds.has(e) ? v`<span class="new-badge ${D("new-badge-text")}">NEW</span>` : "";
	}
	_renderAttrList(e) {
		return v`
      <ul class="attr-list ${D("dialog-field-note")}">
        ${e.map(([e, t]) => v`<li>${oa(e, t)}</li>`)}
      </ul>
    `;
	}
	_renderNameLink(e, t) {
		let n = this._tip(this._nameHover(e));
		return v`<button class="entity-link-primary ${bn()}" data-tip="act" aria-describedby=${n.id} @click=${() => this._openEdit(e)}>${t}</button>${n.desc}`;
	}
	_nameHover(e) {
		switch (e.kind) {
			case "appliance": return this._applianceNameHover(e.entity);
			case "co": return this._coNameHover(e.entity);
			case "uo": return Fi({
				name: e.entity.name,
				area: this._uoArea(e.entity),
				note: e.entity.location_note,
				socketCount: e.entity.socket_count,
				socketsInUse: e.entity.sockets_in_use
			});
		}
	}
	_renderMention(e, t) {
		let n = e.target;
		if (n === null) return e.text;
		let r = this._nameHover(n);
		if (t !== null) {
			let n = this._tip({
				...r,
				action: yl[t],
				blocked: !0
			});
			return v`<span class="dialog-link held" tabindex="0" data-tip="info" aria-describedby=${n.id}>${e.text}</span>${n.desc}`;
		}
		let i = this._tip(r);
		return v`<button class="dialog-link ${bn()} ${O("clickable-outline")}" data-tip="act" aria-describedby=${i.id} @click=${() => this._followLink(n)}>${e.text}</button>${i.desc}`;
	}
	_editHold() {
		let e = [this._editing, this._editingSocket].filter((e) => e !== null);
		return e.some((e) => e.saving) ? "saving" : e.some(dr) ? "dirty" : null;
	}
	_applianceNameHover(e) {
		let t = this._helpers(), n = t ? Ri(e, t) : null, r = n?.kind === "co_socket" ? n.co : null;
		return Pi({
			name: e.name,
			type: e.type,
			pluggedInto: t ? jr(e, t)?.text ?? null : null,
			uoName: r && t ? Ai(r, t) : null,
			effectiveArea: r?.effective_ha_area_id ? M(this._areas.names, r.effective_ha_area_id) : null,
			description: e.description
		});
	}
	_helpers() {
		let e = this._state;
		return e ? (this._helpersCache?.state !== e && (this._helpersCache = {
			state: e,
			h: V(e)
		}), this._helpersCache.h) : null;
	}
	_maybeDebugBadge() {
		return this._debugMode ? v`<span class="debug-mode-badge ${D("debug-badge-text")}">DEBUG</span>` : "";
	}
	get _buildStamp() {
		return cn(this._debugMode, this._build);
	}
	_renderDeleteButton(e) {
		if (!this._debugMode || e.kind === "co_socket") return "";
		let t = e.kind, n = this._tip(K(t, bl(e), { action: "Delete (debug)" }));
		return v`<button
      class="debug-delete-btn ${D("debug-delete-label")}"
      data-tip="act"
      aria-describedby=${n.id}
      aria-label="Debug: delete this ${W[t]}"
      @click=${() => this._openDeleteConfirm(e)}
    >
      <svg class="debug-delete-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="${Zc}"></path>
      </svg>
      <span class="debug-delete-label">Delete</span>
    </button>${n.desc}`;
	}
	_renderMenu() {
		return An({
			open: this._menuOpen,
			tip: this._plainTip("Menu"),
			topEntries: wn,
			groups: Tn
		}, (e) => this._menuIconPath(e), {
			toggle: () => this._toggleMenu(),
			choose: (e) => this._chooseMenuAction(e),
			openSettings: () => {
				this._closeMenu(), this._openSettings();
			}
		});
	}
	_menuIconPath(e) {
		return e === "uo" ? xa[this._socketRegion] : ul[e];
	}
	_renderConfirmDialog(e, t) {
		return v`
      <dialog
        class="${e.className} ${A("modal-dialog-box")}"
        @close=${() => e.onClose()}
        @cancel=${(t) => {
			e.isSaving() && t.preventDefault();
		}}
      >
        ${t ? v`
              <div class="dialog-body">
                ${k(t.title, this._buildStamp)}
                <p class=${O("supporting-text")}>${t.message}</p>
                ${t.lines.length > 0 ? v`<ul class="consequence-list ${O("small-text")}">
                        ${t.lines.map((e) => v`<li>${e}</li>`)}
                      </ul>` : ""}
                ${t.error ? v`<p class="error ${O("error-text")}">${t.error}</p>` : ""}
              </div>
              <p class="${t.warning.className} ${O(t.warning.tone)}"><strong class=${O("emphasis")}>${t.warning.text}</strong></p>
              <div class="dialog-actions">
                <button @click=${() => e.onClose()}>Cancel</button>
                <button class=${t.confirm.className} ?disabled=${e.isSaving()} @click=${() => t.confirm.onClick()}>
                  ${t.confirm.label}
                </button>
              </div>
            ` : ""}
      </dialog>
    `;
	}
	_renderDeleteConfirmDialog() {
		let e = this._deleting;
		return this._renderConfirmDialog({
			className: "delete-dialog",
			onClose: () => this._closeDeleteConfirm(),
			isSaving: () => this._deleting?.saving ?? !1
		}, e && {
			title: W[e.kind],
			message: e.message,
			lines: [],
			error: e.error,
			warning: {
				className: "irreversible-warning",
				tone: "error-text",
				text: "!! This cannot be undone !!"
			},
			confirm: {
				className: "danger",
				label: "Delete",
				onClick: () => this._confirmDelete()
			}
		});
	}
	_renderFlushConfirmDialog() {
		let e = this._flushConfirm;
		return this._renderConfirmDialog({
			className: "flush-dialog",
			onClose: () => this._closeFlushConfirm(),
			isSaving: () => this._flushConfirm?.saving ?? !1
		}, e && {
			title: "Flush",
			message: e.message,
			lines: e.lines,
			error: e.error,
			warning: {
				className: "irreversible-warning",
				tone: "error-text",
				text: "!! This cannot be undone !!"
			},
			confirm: {
				className: "danger",
				label: "Flush",
				onClick: () => this._confirmFlush()
			}
		});
	}
	_renderCommitConfirmDialog() {
		let e = this._commitConfirm;
		return this._renderConfirmDialog({
			className: "commit-dialog",
			onClose: () => this._closeCommitConfirm(),
			isSaving: () => this._commitConfirm?.saving ?? !1
		}, e && {
			title: "Commit",
			message: e.message,
			lines: e.lines,
			error: e.error,
			warning: {
				className: "write-warning",
				tone: "warning-text",
				text: "!! This will write to the live system !!"
			},
			confirm: {
				className: "go",
				label: "Commit",
				onClick: () => this._confirmCommit()
			}
		});
	}
	_renderExportDialog() {
		let e = this._editSession ? Ft(this._editSession.commit_entries.length) : null;
		return mn(this._exporting, e, {
			close: () => this._closeExport(),
			cancel: (e) => {
				this._exporting?.saving && e.preventDefault();
			},
			setFormat: (e) => this._updateExport({ format: e }),
			setIncludeHistory: (e) => this._updateExport({ includeHistory: e }),
			run: () => this._runExport()
		}, this._buildStamp);
	}
	_renderFromNamesDialog() {
		return nc(this._fromNames, {
			close: () => this._closeFromNames(),
			cancel: (e) => {
				this._fromNames?.saving && e.preventDefault();
			},
			setFilter: (e) => this._setFromNamesFilter(e),
			setTicks: (e) => this._setFromNamesTicks(e),
			toggleRow: (e) => this._toggleFromNamesRow(e),
			editName: (e, t) => this._editFromNamesName(e, t),
			apply: () => void this._applyFromNames()
		}, {
			renderStagingButton: (e) => this._renderStagingButton(e),
			renderDialogFilter: (e, t, n) => this._renderDialogFilter(e, t, n)
		}, this._buildStamp);
	}
	_renderWallBatchDialog() {
		let e = this._state, t = this._wallBatch;
		return fo(e && t ? {
			dialog: t,
			state: e,
			rows: this._wallBatchRows(),
			areaNames: this._areas.names
		} : null, {
			close: () => this._closeWallBatch(),
			cancel: (e) => {
				this._wallBatch?.saving && e.preventDefault();
			},
			setFilter: (e) => this._setWallBatchFilter(e),
			setChoices: (e) => this._setWallBatchChoices(e),
			toggleRow: (e) => this._toggleWallBatchRow(e),
			chooseRow: (e, t) => this._chooseWallBatch(e, t),
			editName: (e, t) => this._editWallBatchName(e, t),
			apply: () => void this._applyWallBatch()
		}, {
			renderStagingButton: (e) => this._renderStagingButton(e),
			renderDialogFilter: (e, t, n) => this._renderDialogFilter(e, t, n)
		}, this._buildStamp);
	}
	_renderDiscoveredDialog() {
		return sc(this._discovered && this._state ? na(this._discovered, this._state, this._registries()) : null, () => {
			this._discovered = null;
		}, {
			renderMention: (e) => this._renderMention(e, null),
			renderAttrList: (e) => this._renderAttrList(e)
		}, this._buildStamp);
	}
	_renderHostingMark() {
		return v`<svg class="link-icon hosting-mark" viewBox="0 0 24 24" aria-hidden="true">
      <path d="${Jc}"></path>
    </svg>`;
	}
	_renderMeterIcon() {
		return v`<svg class="meter-icon" viewBox="0 0 24 24" role="img" aria-label="Metered">
      <path d="${Xc}"></path>
    </svg>`;
	}
	_renderSocketIdentity(e) {
		return e.monitoring_entity_registry_id === null ? "" : this._renderMeterIcon();
	}
	_renderSocketLinkButton(e, t, n) {
		return this._renderLinkButton(t ? {
			kind: "appliance",
			entity: t
		} : {
			kind: "co_socket",
			entity: e
		}, n);
	}
	_linkIconPath(e) {
		switch (e) {
			case "plug": return Wc;
			case "unplug": return qc;
			case "socket": return xa[this._socketRegion];
			case "hosting": return Jc;
			case "hosted": return Yc;
		}
	}
	_renderOccupantName(e, t, n) {
		return e ? this._renderNameLink({
			kind: "appliance",
			entity: e
		}, n) : t ? this._renderNameLink({
			kind: "co",
			entity: t
		}, n) : n;
	}
	_renderDepartingName(e, t, n) {
		let r = Vc(e.co_socket_id, e.occupant_device_id === null && e.plugged_into_appliance_id === null, t);
		if (r === null) return "";
		let i = r.kind === "appliance" ? n.applianceNames : n.coNames;
		return v`<s class="departing ${O("supporting-text", "strike-through")}">${N(i, r.subjectId)}</s>`;
	}
	_renderLinkButton(e, t) {
		let n = Us(e, t), r = this._linkIconPath(n.iconKind), i = this._tip(n.hover);
		return v`<button
      class="link-btn ${n.linked ? "linked" : ""} ${n.disabled ? "unavailable" : ""}"
      data-tip="act"
      aria-describedby=${i.id}
      aria-label="${n.ariaLabel}"
      ?disabled=${n.disabled}
      @click=${() => this._openLink(e)}
    >
      <svg class="link-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="${r}"></path>
      </svg>
    </button>${i.desc}`;
	}
	_openLink(e) {
		if (!this._state) return;
		let t = V(this._state);
		switch (this._linkRoomFilter = null, this._linkCoFilter = Uo, e.kind) {
			case "appliance":
				this._linking = xs(e.entity, t);
				return;
			case "co":
				this._linking = Ds(e.entity, t);
				return;
			case "co_socket":
				this._linking = Os(e.entity, t);
				return;
			case "uo":
				this._linking = ks(e.entity, t);
				return;
		}
	}
	_closeLink() {
		this._linking = null;
	}
	_setLinkSelection(e) {
		!this._linking || this._linking.view !== "picker" || (this._linking = {
			...this._linking,
			selectedId: e
		});
	}
	async _submitLink() {
		let e = this._linking;
		if (!e || e.view !== "picker" || e.selectedId === null || !this.hass) return;
		let t = e.candidates.find((t) => t.id === e.selectedId);
		if (!t || t.disabledBy !== null) return;
		let n = cs(e, t);
		this._linking = {
			...e,
			saving: !0,
			error: null
		};
		try {
			await this.hass.callWS(n), this._closeLink(), await this._refresh();
		} catch (e) {
			this._linking = fr(this._linking, e), await this._refresh();
		}
	}
	async _submitUnlink() {
		let e = this._linking;
		if (!e || e.view !== "picker" || !e.unlink || !this.hass) return;
		let t = e.unlink;
		this._linking = {
			...e,
			saving: !0,
			error: null
		};
		try {
			await this.hass.callWS({
				type: t.wsType,
				...t.payload
			}), this._closeLink(), await this._refresh();
		} catch (e) {
			this._linking = fr(this._linking, e), await this._refresh();
		}
	}
	_toggleUoRow(e) {
		if (!this._linking || this._linking.view !== "multi") return;
		let t = new Set(this._linking.selectedIds);
		t.has(e) ? t.delete(e) : t.add(e), this._linking = {
			...this._linking,
			selectedIds: t
		};
	}
	_toggleUoCandidateRow(e) {
		if (!this._linking || this._linking.view !== "multi") return;
		let t = new Set(this._linking.selectedCandidateIds);
		t.has(e) ? t.delete(e) : t.add(e), this._linking = {
			...this._linking,
			selectedCandidateIds: t
		};
	}
	_renderUoKind(e, t) {
		let n = ns(e, t);
		return n === null ? "" : v` <span class=${O("ob-element-name")}>${n}</span>`;
	}
	_renderRowPowering(e) {
		return e.length === 0 ? "" : v`<p class="candidate-note ${D("dialog-field-note")}">
      <span class=${D("dialog-field-prompt")}>${Io}</span> ${e.join(", ")}
    </p>`;
	}
	async _submitMultiApply() {
		let e = this._linking;
		if (!e || e.view !== "multi" || !this.hass) return;
		let t = e.rows.filter((t) => !e.selectedIds.has(t.deviceId)), n = e.candidates.filter((t) => e.selectedCandidateIds.has(t.deviceId));
		if (t.length === 0 && n.length === 0) return;
		this._linking = {
			...e,
			saving: !0,
			error: null
		};
		let r = this.hass, i = await Js([...t.map((e) => ({
			item: {
				kind: "unplug",
				deviceId: e.deviceId,
				label: e.label
			},
			message: ds(e)
		})), ...n.map((t) => ({
			item: {
				kind: "plug-in",
				deviceId: t.deviceId,
				label: t.label
			},
			message: us(e.subjectId, t)
		}))], (e) => r.callWS(e)), a = (e) => i.filter(({ item: t }) => t.kind === e).map(({ item: e, error: t }) => ({
			deviceId: e.deviceId,
			label: e.label,
			message: P(t)
		})), o = a("unplug"), s = a("plug-in");
		if (await this._refresh(), o.length === 0 && s.length === 0) {
			this._closeLink();
			return;
		}
		if (!this._state) {
			this._closeLink();
			return;
		}
		let c = V(this._state), l = c.uosById.get(e.subjectId);
		if (!l) {
			this._closeLink();
			return;
		}
		this._linking = qs(l, c, {
			failures: o,
			candidateFailures: s,
			filter: e.filter
		});
	}
	_pickerDialogTitle(e, t) {
		return v`<span class=${O("ob-element-name")}>${e}</span> ${t.subjectLabel}`;
	}
	_setLinkRoomFilter(e) {
		this._pinLinkRows(), this._linkRoomFilter = e;
		let t = this._linking, n = this._linkCoFilter;
		t && t.view === "picker" && n.kind === "co" && (Po(t, e).some((e) => e.coId === n.coId) || (this._linkCoFilter = Uo));
	}
	_setLinkCoFilter(e) {
		if (this._pinLinkRows(), this._linkCoFilter = e, e.kind === "co") {
			let t = this._linking;
			if (t && t.view === "picker" && t.kind === "appliance") {
				let n = t.candidates.find((t) => t.coId === e.coId);
				n && (this._linkRoomFilter = n.uoName);
			}
		}
	}
	_pinLinkRows() {
		this._linking &&= Zo(this._linking);
	}
	_setLinkFilter(e) {
		this._linking &&= {
			...Zo(this._linking),
			filter: e
		};
	}
	_renderDialogFilter(e, t, n, r = "") {
		return v`<div class="dialog-filter">
      ${r}<input
        type="search"
        class="dialog-filter-input"
        aria-label="Filter the rows"
        placeholder="Filter…"
        .value=${e}
        ?disabled=${t}
        @input=${(e) => n(e.target.value)}
      />
    </div>`;
	}
	_renderLinkFilterSelect(e, t, n, r, i) {
		return v`
      <div class="edit-field">
        <label for=${e} class=${D("dialog-field-prompt")}>${t}</label>
        <select
          id=${e}
          @change=${(e) => i(e.target.value)}
        >
          ${n.map((e) => v`<option value=${e.value} .selected=${r === e.value}>${e.text}</option>`)}
        </select>
      </div>
    `;
	}
	_renderCandidateItems(e, t) {
		let n = [], r = 0;
		for (; r < t.length;) {
			let i = t[r].groupKey;
			if (i === null) {
				n.push(this._renderCandidateRow(e, t[r])), r += 1;
				continue;
			}
			let a = t[r].groupLabel, o = [];
			for (; r < t.length && t[r].groupKey === i;) o.push(t[r]), r += 1;
			n.push(v`
        <li class="candidate-group">
          <div class="candidate-group-label ${D("dialog-field-note", "emphasis")}">${a === null ? "" : Lo(a)}</div>
          ${Bo(o[0]) === null ? "" : v`<div class="candidate-context group-context ${D("dialog-field-note")}">${Bo(o[0])}</div>`}
          <ul class="candidate-group-items">
            ${o.map((t) => this._renderCandidateRow(e, t))}
          </ul>
        </li>
      `);
		}
		return n;
	}
	_renderUoIdentity(e) {
		return v`${this._renderNameLink({
			kind: "uo",
			entity: e
		}, e.name)}${this._renderAttrList(sa(e, this._uoArea(e)))}`;
	}
	_uoArea(e) {
		return M(this._areas.names, e.ha_area_id);
	}
	_renderCoCandidateLists(e, t, n) {
		let r = Es(Yo(e)), i = Es(t), a = (t, n, r, i, a, o) => v`<section class="link-list" data-list=${t} aria-label=${n}>
        ${r}
        ${i.length === 0 ? v`<p class="no-candidates ${D("dialog-field-note")}">${o}</p>` : this._renderCandidateList(e, a)}
      </section>`;
		return v`<div class="link-lists ${this._linkListsSideBySide(e) ? "side-by-side" : ""}">
      ${a("outlets", "Wall Sockets", ((e) => v`<h4 class="link-list-title ${D("dialog-field-note")}">${e}</h4>`)("Wall Sockets"), r.outlets, i.outlets, In)}${a("sockets", "Smart device sockets", n, r.sockets, i.sockets, Ln)}
    </div>`;
	}
	_renderCandidateList(e, t) {
		return t.length > 0 ? v`<ul class="link-candidates">${this._renderCandidateItems(e, t)}</ul>` : v`<p class="no-candidates ${D("dialog-field-note")}">${Fn}</p>`;
	}
	_renderCandidateRow(e, t) {
		return v`
      <li>
        <label class="choice-row ${O("small-text")}">
          <input
            type="radio"
            name="link-candidate"
            .checked=${e.selectedId === t.id}
            ?disabled=${t.disabledBy !== null}
            @change=${() => this._setLinkSelection(t.id)}
          />
          <span class=${t.disabledBy === null ? "" : O("disabled-text")}>${Ro(t)}</span>
        </label>
        ${zo(t) === null ? "" : v`<p class="candidate-context ${D("dialog-field-note")}">${zo(t)}</p>`}
        ${t.note === null ? "" : v`<p class="candidate-note ${D("dialog-field-note")}">
              <span class=${D("dialog-field-prompt")}>${Fo}</span> ${t.note}
            </p>`}
      </li>
    `;
	}
	_renderPickerDialogBody(e) {
		let t = e.saving ? "saving" : null, n = Qs(e, {
			room: this._linkRoomFilter,
			co: this._linkCoFilter
		}), { roomOptions: r, coOptions: i, offeredCount: a } = n, o = i.length > 0 ? this._renderLinkFilterSelect("link-filter-co", "Smart Device:", [
			{
				value: Wo(Uo),
				text: "All available"
			},
			{
				value: Wo({ kind: "all" }),
				text: "All"
			},
			...i.map((e) => ({
				value: Wo({
					kind: "co",
					coId: e.coId
				}),
				text: e.text
			}))
		], Wo(this._linkCoFilter), (e) => this._setLinkCoFilter(Go(e))) : "", s = n.hasFilterBar ? this._renderDialogFilter(e.filter, e.saving, (e) => this._setLinkFilter(e), n.showsDropdownsInBar ? v`<div class="link-filters">
              ${r.length > 0 ? this._renderLinkFilterSelect("link-filter-room", "Room:", [{
			value: "",
			text: "All"
		}, ...r.map((e) => ({
			value: e,
			text: e
		}))], this._linkRoomFilter ?? "", (e) => this._setLinkRoomFilter(e === "" ? null : e)) : ""}
              ${o}
            </div>` : "") : "", c = n.socketsHeading === "title" ? v`<h4 class="link-list-title ${D("dialog-field-note")}">Smart device sockets</h4>` : v`<div class="link-filters">${o}</div>`;
		return v`
      <div class="dialog-body">
        ${k(v`${this._pickerDialogTitle(n.titleLabel, e)}${this._renderHaDeviceIconLink(e.subjectHaDevice, "inline")}`, this._buildStamp)}
        ${e.currentLabel === null ? "" : v`<p class="plugged-into ${D("dialog-field-note")}">
              <span class=${D("dialog-field-prompt")}>${n.currentWord}</span>
              ${this._renderMention(e.currentLabel, t)}${this._renderHaDeviceIconLink(e.currentHaDevice, "inline")}
            </p>`}
        ${e.powering.length > 0 ? v`<p class="plugged-into ${D("dialog-field-note")}"><span class=${D("dialog-field-prompt")}>Powering:</span> ${e.powering.map((e, n) => v`${n > 0 ? ", " : ""}${this._renderMention(e, t)}`)}</p>` : ""}
        ${e.contextLabel === null ? "" : e.contextLabel.placeName === null ? v`<p class="plugged-into ${D("dialog-field-note")}">Not plugged in currently.</p>` : v`<p class="plugged-into ${D("dialog-field-note")}">
                <span class=${D("dialog-field-prompt")}>Plugged into:</span> ${this._renderMention(e.contextLabel.placeName, t)}${this._renderHaDeviceIconLink(e.contextLabel.placeHaDevice, "inline")}
              </p>`}
        ${n.loneCandidate ? v`<p class="lone-candidate ${O("supporting-text")}"><span class=${D("dialog-field-prompt")}>${Mo(e)}:</span> ${e.candidates[0].fullLabel}</p>` : a > 0 ? v`
                <p class=${D("dialog-section")}>
                  ${n.listHeading}
                </p>
                ${s}
                ${e.kind === "co" ? this._renderCoCandidateLists(e, n.visible, c) : this._renderCandidateList(e, n.visible)}
              ` : ""}
        ${e.error ? v`<p class="error ${O("error-text")}">${e.error}</p>` : ""}
      </div>
      <div class="dialog-actions">
        <button autofocus @click=${() => this._closeLink()}>Cancel</button>
        ${e.unlink ? this._renderStagingButton({
			label: e.unlink.label,
			tip: ll,
			className: "danger",
			disabled: n.unplugBusy ? to : !1,
			onClick: () => this._submitUnlink()
		}) : ""}
        ${n.primary === null ? "" : this._renderStagingButton({
			label: n.primary.label,
			tip: ll,
			disabled: n.primary.disabled !== null && Uc[n.primary.disabled],
			onClick: () => this._submitLink()
		})}
      </div>
    `;
	}
	_renderMultiDialogBody(e) {
		let t = as(e), n = os(e), r = ts(e.rows), i = ts(e.candidates), a = v`<p class="no-candidates ${D("dialog-field-note")}">${Fn}</p>`, o = e.rows.length + e.candidates.length > 1 ? this._renderDialogFilter(e.filter, e.saving, (e) => this._setLinkFilter(e)) : "";
		return v`
      <div class="dialog-body uo-picker">
        ${k(v`<span class=${O("ob-element-name")}>Wall Socket:</span> ${e.subjectLabel}`, this._buildStamp)}
        ${e.candidates.length > 0 ? "" : o}
        ${e.rows.length > 0 ? v`
              <p class=${D("dialog-section")}>Currently plugged in:</p>
              ${t.length === 0 ? a : v`<ul class="link-candidates">
                ${t.map((t) => {
			let n = e.failures.find((e) => e.deviceId === t.deviceId);
			return v`
                    <li>
                      <label class="choice-row ${O("small-text")}">
                        <input
                          type="checkbox"
                          .checked=${e.selectedIds.has(t.deviceId)}
                          @change=${() => this._toggleUoRow(t.deviceId)}
                        />
                        <span>${t.label}</span>${this._renderUoKind(t.kind, r)}
                      </label>
                      ${this._renderRowPowering(t.powering)}
                      ${n ? v`<p class="link-row-error ${D("dialog-field-note", "error-text")}">${n.message}</p>` : ""}
                    </li>
                  `;
		})}
              </ul>`}
            ` : ""}
        ${e.candidates.length > 0 ? v`
              <p class=${D("dialog-section")}>Available to plug in:</p>
              ${o}
              ${n.length === 0 ? a : v`<ul class="link-candidates">
                ${n.map((t) => {
			let n = e.candidateFailures.find((e) => e.deviceId === t.deviceId);
			return v`
                    <li>
                      <label class="choice-row ${O("small-text")}">
                        <input
                          type="checkbox"
                          .checked=${e.selectedCandidateIds.has(t.deviceId)}
                          @change=${() => this._toggleUoCandidateRow(t.deviceId)}
                        />
                        <span>${t.label}</span>${this._renderUoKind(t.kind, i)}
                      </label>
                      ${n ? v`<p class="link-row-error ${D("dialog-field-note", "error-text")}">${n.message}</p>` : ""}
                    </li>
                  `;
		})}
              </ul>`}
            ` : ""}
        ${e.error ? v`<p class="error ${O("error-text")}">${e.error}</p>` : ""}
      </div>
      <div class="dialog-actions">
        <button autofocus @click=${() => this._closeLink()}>Cancel</button>
        ${this._renderStagingButton({
			label: "Apply",
			tip: ll,
			disabled: e.saving ? to : Gs(e) ? io : !1,
			onClick: () => this._submitMultiApply()
		})}
      </div>
    `;
	}
	_linkListsSideBySide(e) {
		return e.kind !== "co" || this._layoutTier === "narrow" ? !1 : Yo(e).length > 0;
	}
	_renderLinkDialog() {
		let e = this._linking;
		return v`
      <dialog
        class="link-dialog ${e !== null && e.view === "picker" && this._linkListsSideBySide(e) ? "side-by-side" : ""} ${A("modal-dialog-box")}"
        @close=${() => this._closeLink()}
        @cancel=${(e) => {
			this._linking?.saving && e.preventDefault();
		}}
      >
        ${e ? e.view === "picker" ? this._renderPickerDialogBody(e) : this._renderMultiDialogBody(e) : ""}
      </dialog>
    `;
	}
	_renderSocketsList(e) {
		if (!this._state) return "";
		let t = V(this._state), n = this._editHold(), r = Bc(this._state, this._editSession), i = [...t.socketsByCo.get(e) ?? []].sort((e, t) => e.position - t.position);
		if (i.length === 0) return "";
		let a = i.length === 1 ? "Socket" : "Sockets";
		return v`<div class="socket-list" role="group" aria-label=${a}>
      <p class=${D("dialog-section")}>${a}</p>
      <ul>
        ${i.map((e) => {
			let i = Ei(e, t), a = r.coSocket.get(e.co_socket_id), o = {
				text: i.name,
				target: i.appliance ? {
					kind: "appliance",
					entity: i.appliance
				} : i.co ? {
					kind: "co",
					entity: i.co
				} : null
			};
			return v`<li class="socket-list-line">
            <span class="socket-list-meter">${this._renderSocketIdentity(e)}</span>
            <span class="socket-list-occupant ${O("supporting-text")}">${a ? this._renderPendingMarker(this._pendingMarkerText(a, t)) : ""}${this._renderMention(o, n)}${this._renderDepartingName(e, r, t)}</span>
            <button
              class="plain-btn"
              aria-label="Edit ${e.alias}"
              @click=${() => this._openSocketEdit(e)}
            >
              Edit
            </button>
          </li>`;
		})}
      </ul>
    </div>`;
	}
	_renderEditDialog(e) {
		let t = this[e];
		return v`
      <dialog
        class="${xl[e]} ${A("modal-dialog-box")}"
        @close=${(t) => {
			t.target.open || this._closeEdit(e);
		}}
        @cancel=${(t) => {
			this[e]?.saving && t.preventDefault();
		}}
      >
        ${t ? v`
              <div class="dialog-body">
                ${k(v`<span class=${O("ob-element-name")}>${W[t.kind]}:</span>
                  ${t.draft[wr[t.kind].requiredField]}${t.kind === "appliance" ? this._renderHaItems(t.id) : ""}
                  ${this._renderHaDeviceIconLink(t.titleHaDevice, "edge")}`, this._buildStamp)}
                ${t.pluggedInto === void 0 ? "" : v`<p class="plugged-into ${D("dialog-field-note")}">
                      ${t.pluggedInto === null ? v`<span class=${O("ob-element-name")}>Unplugged</span>` : v`<span class=${D("dialog-field-prompt")}>Plugged into:</span> ${this._renderMention(t.pluggedInto, this._editHold())}${this._renderHaDeviceIconLink(t.pluggedIntoHaDevice, "inline")}`}
                    </p>`}
                ${Object.keys(t.draft).map((n, r) => v`
                    <div class="edit-field">
                      <label class=${D("dialog-field-prompt")}>${_r[n] ?? n}</label>
                      ${vr.has(n) ? this._renderAreaSelect(t.draft[n], (t) => this._updateDraftField(e, n, t), t.inheritLabel ?? vr.get(n)) : v`<input
                            ?autofocus=${r === 0}
                            type=${br.has(n) ? "number" : "text"}
                            .step=${br.has(n) ? "1" : ""}
                            .value=${t.draft[n]}
                            @input=${(t) => this._updateDraftField(e, n, t.target.value)}
                          />`}
                    </div>
                  `)}
                ${t.kind === "co" ? this._renderSocketsList(t.id) : ""}
                <ul class="entity-id ${D("dialog-metadata")}">
                  <li class="id-row"><span class=${O("ob-element-name")}>id</span>: ${t.id}</li>
                  ${t.readonlyFields.map(([e, t]) => v`<li><span class=${O("ob-element-name")}>${e}</span>: ${t}</li>`)}
                  ${t.kind === "co" ? this._renderHaDeviceLink(t.id) : ""}
                </ul>
                ${t.error ? v`<p class="error ${O("error-text")}">${t.error}</p>` : ""}
              </div>
              <div class="dialog-actions">
                <button @click=${() => this._closeEdit(e)}>Cancel</button>
                <button
                  ?disabled=${t.saving || !this._isEditValid(t)}
                  @click=${() => this._saveEdit(e)}
                >
                  Save
                </button>
              </div>
            ` : ""}
      </dialog>
    `;
	}
	_renderHaDeviceLink(e) {
		return v`<li class="ha-device-link ${D("dialog-field-note")}">
      ${this._renderHaDeviceAnchor(e, "ha-device-text-link", "Open in Home Assistant", void 0)}
    </li>`;
	}
	_renderHaDeviceIconLink(e, t) {
		if (e === null) return "";
		let n = this._state?.cos.find((t) => t.co_id === e)?.alias ?? "device", r = this._renderHaDeviceAnchor(e, `ha-device-icon-link ${t}`, "", `Open ${n} in Home Assistant`);
		return t === "inline" ? v`<span class="ha-gap"> </span>${r}` : r;
	}
	_renderHaDeviceAnchor(e, t, n, r) {
		return this._renderHaAnchor(`/config/devices/device/${encodeURIComponent(e)}`, t, n, r);
	}
	_customPanel() {
		try {
			return window.parent.customPanel;
		} catch {
			return;
		}
	}
	_openInHomeAssistant(e) {
		let t = this._customPanel();
		t === void 0 ? window.parent.location.assign(e) : t.navigate(e);
	}
	_topLocation() {
		try {
			let { pathname: e, search: t } = window.parent.location;
			return {
				pathname: e,
				search: t
			};
		} catch {
			return window.location;
		}
	}
	_renderHaItems(e) {
		let t = (this._haItems[e] ?? []).length > 0, n = this._plainTip(t ? `List the entities for ${this._applianceName(e)}` : this._noHaItemsReason(e));
		return v`<span class="ha-items-wrap"
      ><button
        class="ha-items-btn ${t ? bn() : O("disabled-text")}"
        data-tip="act"
        aria-label="Home Assistant items"
        aria-haspopup="dialog"
        aria-describedby=${n.id}
        ?disabled=${!t}
        @click=${() => this._setHaItemsOpen(!0)}
      >
        <svg class="ha-items-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="${rl}"></path>
        </svg>
        <svg class="ha-items-icon" viewBox="0 0 24 24" aria-hidden="true">
          <path d="${nl}"></path>
        </svg></button
      >${n.desc}</span
    >`;
	}
	_applianceName(e) {
		return N(this._helpers()?.applianceNames ?? /* @__PURE__ */ new Map(), e);
	}
	_haItemsContent() {
		let e = this._editing;
		return e?.kind !== "appliance" || !e.haItemsOpen ? null : {
			name: this._applianceName(e.id),
			layout: ac(this._haItems[e.id] ?? []),
			renderItem: this._renderHaItem
		};
	}
	_noHaItemsReason(e) {
		let t = this._helpers()?.appliancesById.get(e);
		return t !== void 0 && z(t).kind === "co_socket" ? "Not yet created in Home Assistant" : "Not plugged into a Smart Device, so it has no Home Assistant items";
	}
	_renderHaAnchor(e, t, n, r) {
		return v`<a
        class=${t}
        href=${e}
        target="_top"
        aria-label=${Ye(r)}
        @click=${(t) => {
			let n = this._customPanel();
			n !== void 0 && (t.preventDefault(), n.navigate(e));
		}}
        >${n}${this._renderHaLogo()}</a
      >`;
	}
	_renderHaLogo() {
		return v`<svg class="ha-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="${tl}"></path>
    </svg>`;
	}
	_renderAreaSelect(e, t, n) {
		let r = this._areas.groups, i = (t) => v`<option value=${t.area_id} .selected=${e === t.area_id}>
        ${t.name}
      </option>`;
		return v`
      <select
        @change=${(e) => t(e.target.value)}
      >
        <option value="" .selected=${e === ""}>${n}</option>
        ${r.map((e) => e.label === null ? e.options.map(i) : v`<optgroup label=${e.label}>${e.options.map(i)}</optgroup>`)}
      </select>
      <p class="area-hint ${D("dialog-field-note")}">${yr}</p>
    `;
	}
	_renderCreateDialog() {
		let e = this._creating;
		return v`
      <dialog
        class="create-dialog ${A("modal-dialog-box")}"
        @close=${() => this._closeCreate()}
        @cancel=${(e) => {
			this._creating?.saving && e.preventDefault();
		}}
      >
        ${e ? v`
              <div class="dialog-body">
                ${k(`New ${W[e.kind]}`, this._buildStamp)}
                ${Object.keys(e.draft).map((t) => v`
                    <div class="edit-field">
                      <label class=${D("dialog-field-prompt")}>${_r[t] ?? t}</label>
                      ${t === "ha_area_id" ? this._renderAreaSelect(e.draft.ha_area_id, (e) => this._updateCreateDraftField("ha_area_id", e), "— none —") : v`<input
                            type="text"
                            .value=${e.draft[t]}
                            @input=${(e) => this._updateCreateDraftField(t, e.target.value)}
                          />`}
                    </div>
                  `)}
                ${e.error ? v`<p class="error ${O("error-text")}">${e.error}</p>` : ""}
              </div>
              <div class="dialog-actions">
                <button @click=${() => this._closeCreate()}>Cancel</button>
                <button
                  ?disabled=${e.saving || !this._isCreateValid(e)}
                  @click=${() => this._saveCreate()}
                >
                  Create
                </button>
              </div>
            ` : ""}
      </dialog>
    `;
	}
	_renderPowerIcon(e, t, n) {
		return v`<svg class="th-icon ${n ?? ""}" viewBox="0 0 24 24" role="img" aria-label="${t}">
      <path d="${e}"></path>
    </svg>`;
	}
	_setThemeOverride(e) {
		this._themeOverride = e;
		try {
			localStorage.setItem(ti, e);
		} catch {}
	}
	_toggleSectionCollapse(e) {
		let t = new Set(this._collapsedSections);
		t.has(e) ? t.delete(e) : t.add(e), this._collapsedSections = t, gi(t);
	}
	_renderSectionCollapseToggle(e, t, n) {
		let r = !n && this._collapsedSections.has(e), i = this._tip(Yi(e, t, Ki(n, r)));
		return v`<div class="section-toggle-row"><button
      class="section-collapse-btn ${D("table-division-heading")}"
      data-tip="act"
      aria-describedby=${i.id}
      aria-expanded="${!r}"
      ?disabled=${n}
      @click=${() => this._toggleSectionCollapse(e)}
    >
      <svg class="collapse-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="${r ? $c : Qc}"></path>
      </svg>
      <span class="tooltip-cue">${fi[e]}</span>
    </button>${i.desc}${this._renderSectionInfoButton(fi[e], Yi(e, t, "info"))}</div>`;
	}
	_renderSectionInfoButton(e, t) {
		let n = this._tip(t);
		return v`<button
      type="button"
      class="info-btn ${D("info-cue")}"
      data-tip="info"
      aria-label="Counts for ${e}"
      aria-describedby=${n.id}
    >i</button>${n.desc}`;
	}
	_toggleCardBandGroup(e, t) {
		let n = {
			...this._collapsedCardBandGroups,
			[e]: new Set(this._collapsedCardBandGroups[e])
		}, r = n[e];
		r.has(t) ? r.delete(t) : r.add(t), this._collapsedCardBandGroups = n, Si(n);
	}
	_renderCardBandGroupToggle(e, t, n, r) {
		let i = !r && this._collapsedCardBandGroups[e].has(t), a = this._tip(Zi(e, t, n, Ki(r, i)));
		return v`<div class="section-toggle-row"><button
      class="section-collapse-btn ${D("table-division-heading")}"
      data-tip="act"
      aria-describedby=${a.id}
      aria-expanded="${!i}"
      ?disabled=${r}
      @click=${() => this._toggleCardBandGroup(e, t)}
    >
      <svg class="collapse-icon" viewBox="0 0 24 24" aria-hidden="true">
        <path d="${i ? $c : Qc}"></path>
      </svg>
      <span class="tooltip-cue">${_i[t]}</span>
    </button>${a.desc}${this._renderSectionInfoButton(_i[t], Zi(e, t, n, "info"))}</div>`;
	}
	_renderThemeRadios() {
		return v`<fieldset class="theme-options">
      <legend class=${D("dialog-field-prompt")}>Theme</legend>
      ${Object.entries($r).map(([e, t]) => v`<label class="theme-option choice-row">
          <input
            type="radio"
            name="theme"
            value=${e}
            .checked=${e === this._themeOverride}
            @change=${() => this._setThemeOverride(e)}
          />
          ${t}${e === "system" ? " (default)" : ""}
        </label>`)}
    </fieldset>`;
	}
	_withTooltipBody(e, t) {
		return t === "" ? e : `${e}\n\n${t}`;
	}
	_tip(e) {
		let t = `tip-${this._tipSeq++}`;
		return {
			id: t,
			desc: v`<span class="tip-text" id=${t} hidden data-hover=${e.icon ?? gl} data-blocked=${e.blocked ? "true" : "false"}>${Zr(e)}</span>`
		};
	}
	_plainTip(e) {
		let t = `tip-${this._tipSeq++}`;
		return {
			id: t,
			desc: v`<span class="tip-text" id=${t} hidden>${e}</span>`
		};
	}
	_renderTrayIcon(e) {
		return v`<svg class="tray-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="${e}"></path></svg>`;
	}
	_renderStagingButton(e) {
		let t = e.disabled !== !1, n = t ? e.disabled.reason : e.tip;
		if (this._mode !== "batch" || n === null) return v`<button
        class="staging-btn ${e.className ?? ""}"
        ?disabled=${t}
        @click=${e.onClick}
      >${this._mode === "batch" ? this._renderTrayIcon(il) : ""}${e.label}</button>`;
		let r = this._plainTip(n);
		return v`<button
      class="staging-btn ${e.className ?? ""}"
      data-tip="act"
      aria-describedby=${r.id}
      ?disabled=${t}
      @click=${e.onClick}
    >${this._renderTrayIcon(il)}${e.label}</button>${r.desc}`;
	}
	_pendingMarkerText(e, t) {
		let n = (e) => {
			let n = t.socketsById.get(e);
			if (n === void 0) return j(null);
			let r = N(t.coNames, n.co_id);
			return (t.socketsByCo.get(n.co_id)?.length ?? 0) > 1 ? `Socket ${Mn(n)} of ${r}` : r;
		}, r = (e) => t.uoNames.has(e) ? `Wall Socket ${N(t.uoNames, e)}` : j(null), i = (e) => e === null ? null : e.kind === "uo" ? r(e.id) : n(e.id), a = e.map((e) => Hc(N(e.kind === "appliance" ? t.applianceNames : t.coNames, e.subjectId), i(e.from), i(e.to)));
		return this._withTooltipBody("Pending:", a.join("\n"));
	}
	_renderPendingMarker(e) {
		let t = this._plainTip(e);
		return v`<button type="button" class="pending-marker ${D("pending-marker")}" data-tip="info" aria-label="Pending change" aria-describedby=${t.id}>*</button>${t.desc}`;
	}
	_renderConsequenceLine(e, t) {
		let n = (e, n) => {
			switch (e) {
				case "appliance": return N(t.applianceNames, n);
				case "co_socket": return N(t.coSocketLabels, n);
				case "co": return N(t.coNames, n);
				case "uo": return N(t.uoNames, n);
			}
		}, r = e.ids.map((e) => n(e.role, e.id));
		switch (e.command) {
			case "create_plugged_into":
			case "assign_co_to_co_socket": return `${e.verb} ${r[0]} into ${r[1]}`;
			case "assign_co_to_uo":
			case "assign_appliance_to_uo": return `${e.verb} ${r[0]} to ${r[1]}`;
			default: return `${e.verb} ${r[0]}`;
		}
	}
	_renderConsequenceLines(e, t) {
		return e.map((e, n) => {
			let [r, ...i] = e.entries.map((e) => this._renderConsequenceLine(e, t));
			return [`${n + 1}. ${r}`, ...i.map((e) => `    ${e}`)].join("\n");
		});
	}
	_renderSessionToolbar(e, t) {
		let n = Fc(e), r = this._withTooltipBody(n.undo.title, this._renderConsequenceLines(Nc(e), t).join("\n")), i = this._withTooltipBody(n.redo.title, this._renderConsequenceLines(Pc(e), t).join("\n")), a = this._withTooltipBody(n.commit.title, this._renderConsequenceLines(jc(e), t).join("\n")), o = this._withTooltipBody(n.flush.title, this._renderConsequenceLines(Mc(e), t).join("\n")), s = this._plainTip(r), c = this._plainTip(i), l = this._plainTip(a), u = this._plainTip(o);
		return v`
      <div class="session-toolbar">
        <button
          class="session-btn ${O("small-text", "emphasis")}"
          data-tip="act"
          aria-describedby=${s.id}
          ?disabled=${n.undo.disabled}
          @click=${() => this._runSessionCommand("outlet_binder/edit_session_undo")}
        >
          ${this._renderTrayIcon(al)}Undo${n.undo.count > 0 ? ` (${n.undo.count})` : ""}
        </button>${s.desc}
        <button
          class="session-btn ${O("small-text", "emphasis")}"
          data-tip="act"
          aria-describedby=${c.id}
          ?disabled=${n.redo.disabled}
          @click=${() => this._runSessionCommand("outlet_binder/edit_session_redo")}
        >
          ${this._renderTrayIcon(ol)}Redo${n.redo.count > 0 ? ` (${n.redo.count})` : ""}
        </button>${c.desc}
        <button
          class="session-btn go ${O("small-text", "emphasis")}"
          data-tip="act"
          aria-describedby=${l.id}
          ?disabled=${n.commit.disabled}
          @click=${() => this._openCommitConfirm(e, t)}
        >
          ${this._renderTrayIcon(sl)}Commit${n.commit.count > 0 ? ` (${n.commit.count})` : ""}
        </button>${l.desc}
        <button
          class="session-btn danger ${O("small-text", "emphasis")}"
          data-tip="act"
          aria-describedby=${u.id}
          ?disabled=${n.flush.disabled}
          @click=${() => this._openFlushConfirm(e, t)}
        >
          ${this._renderTrayIcon(cl)}Flush${n.flush.count > 0 ? ` (${n.flush.count})` : ""}
        </button>${u.desc}
      </div>
    `;
	}
	async _runSessionCommand(e) {
		if (this.hass) {
			this._error = null;
			try {
				await this.hass.callWS({ type: e }), await this._refresh();
			} catch (e) {
				await this._refresh(), this._error = Nn("Edit session command failed", e);
			}
		}
	}
	_openFlushConfirm(e, t) {
		let n = e.undo_group_count + e.redo_group_count;
		this._flushConfirm = {
			message: `Discard ${Ec(n, "staged change")}?`,
			lines: this._renderConsequenceLines(Mc(e), t),
			saving: !1,
			error: null
		};
	}
	_closeFlushConfirm() {
		this._flushConfirm = null;
	}
	async _confirmFlush() {
		let e = this._flushConfirm;
		if (!(!e || !this.hass)) {
			this._flushConfirm = {
				...e,
				saving: !0,
				error: null
			};
			try {
				await this.hass.callWS({ type: "outlet_binder/edit_session_flush" }), this._closeFlushConfirm(), await this._refresh();
			} catch (t) {
				this._flushConfirm = {
					...e,
					saving: !1,
					error: P(t)
				};
			}
		}
	}
	_openCommitConfirm(e, t) {
		this._commitConfirm = {
			message: `Apply ${Ec(e.undo_group_count, "staged change")}?`,
			lines: this._renderConsequenceLines(jc(e), t),
			saving: !1,
			error: null
		};
	}
	_closeCommitConfirm() {
		this._commitConfirm = null;
	}
	async _confirmCommit() {
		let e = this._commitConfirm;
		if (!(!e || !this.hass)) {
			this._commitConfirm = {
				...e,
				saving: !0,
				error: null
			};
			try {
				await this.hass.callWS({ type: "outlet_binder/edit_session_commit" }), this._closeCommitConfirm(), await this._refresh();
			} catch (t) {
				this._commitConfirm = {
					...e,
					saving: !1,
					error: P(t)
				}, await this._refresh();
			}
		}
	}
	render() {
		let e = this._editSession?.failed_entry ?? null, t = this._state ? this._deriveMainView(this._state) : null;
		return this._tipSeq = 0, v`
      ${this._renderEditDialog("_editing")} ${this._renderEditDialog("_editingSocket")} ${this._renderLinkDialog()} ${this._renderCreateDialog()}
      ${this._renderDeleteConfirmDialog()} ${this._renderFlushConfirmDialog()}
      ${this._renderCommitConfirmDialog()}
      ${rc(this._renderThemeRadios(), () => this._closeSettings(), this._buildStamp)}
      ${oc(this._haItemsContent(), () => this._setHaItemsOpen(!1), this._buildStamp)}
      ${this._renderFromNamesDialog()} ${this._renderWallBatchDialog()}
      ${this._renderExportDialog()}
      ${this._renderDiscoveredDialog()}
      ${this._renderHeaderBar()}
      ${this._editSession && t && (this._mode === "batch" || this._editSession.entry_count > 0) ? v`<div class="toolbar-row">
              ${this._renderSessionToolbar(this._editSession, t.h)}
            </div>` : ""}
      ${this._layoutTier !== "wide" && t ? this._renderTabRow(t.state, t.matches) : ""}
      <div class="scroll-region">
        ${this._loading && !this._state ? v`<p class=${O("supporting-text")}>Loading…</p>` : ""}
        ${this._error ? v`<p class="error ${O("error-text")}">${this._error}</p>` : ""}
        ${e ? v`<p class="error ${O("error-text")}">
              Staged change #${e.entry_seq} (${e.command}) failed:
              ${Pn(e.message)} The rows below show state up to that point.
            </p>` : ""}
        ${t ? this._renderStructuredView(t.state, t.h, t.pending, t.matches) : ""}
      </div>
      <div class="tooltip-popover ${A("hover-box")}" popover="manual" aria-hidden="true"></div>
    `;
	}
	_deriveMainView(e) {
		let t = V(e);
		return {
			state: e,
			h: t,
			pending: Bc(e, this._editSession),
			matches: this._mainMatches(e, t)
		};
	}
	_mainTextSources(e) {
		return {
			h: e,
			coModel: (e) => this._coDevice(e),
			uoArea: (e) => this._uoArea(e)
		};
	}
	_mainMatches(e, t) {
		return ba(this._mainFilter, Vi(t), e.appliances, e.uos, this._layoutTier === "narrow" ? "cards" : "table", this._mainTextSources(t));
	}
	_renderHeaderBar() {
		return v`<div class="header-bar">
      <h1 class=${D("page-title")}>${this._maybeDebugBadge()} Outlet &amp; Appliance Binding</h1>
      <div class="header-controls">${this._renderMainFilter()}${this._renderMenu()}</div>
    </div>`;
	}
	_renderMainFilter() {
		let e = this._plainTip("Filter"), t = this._plainTip("Close the filter");
		return eo({
			open: this._filterOpen,
			pos: this._filterPos,
			text: this._mainFilter,
			tip: e,
			closeTip: t
		}, {
			show: () => void this._showMainFilter(),
			close: () => this._closeMainFilter(),
			setText: (e) => {
				this._mainFilter = e;
			},
			startDrag: (e) => this._startFilterDrag(e),
			moveDrag: (e) => this._moveFilterDrag(e),
			endDrag: () => this._endFilterDrag()
		});
	}
	async _showMainFilter() {
		this._filterOpen || (this._filterOpen = !0, await this.updateComplete, this._mainFilterInputEl?.focus());
	}
	_startFilterDrag(e) {
		let t = this._mainFilterEl;
		if (!t) return;
		e.preventDefault();
		let n = t.getBoundingClientRect();
		this._filterDrag = sr({
			x: e.clientX,
			y: e.clientY
		}, n), e.currentTarget.setPointerCapture?.(e.pointerId);
	}
	_moveFilterDrag(e) {
		if (!this._filterDrag) return;
		let t = cr({
			x: e.clientX,
			y: e.clientY
		}, this._filterDrag);
		this._placeMainFilter(t.left, t.top);
	}
	_endFilterDrag() {
		this._filterDrag = null;
	}
	_placeMainFilter(e, t) {
		let n = this._mainFilterEl, r = n?.parentElement;
		if (!n || !r) return;
		let i = n.getBoundingClientRect();
		this._filterPos = lr({
			left: e,
			top: t
		}, {
			width: i.width,
			height: i.height
		}, {
			width: window.innerWidth,
			height: window.innerHeight
		}, r.getBoundingClientRect());
	}
	_keepMainFilterOnScreen() {
		if (!this._filterPos || !this._mainFilterEl) return;
		let e = this._mainFilterEl.getBoundingClientRect();
		this._placeMainFilter(e.left, e.top);
	}
	_closeMainFilter() {
		this._mainFilter = "", this._filterOpen = !1, this._filterPos = null, this._filterDrag = null, this.updateComplete.then(() => this._mainFilterOpenEl?.focus());
	}
	_renderTabRow(e, t) {
		let n = {
			devices: e.cos.length,
			appliances: e.appliances.length,
			uos: e.uos.length
		};
		return v`<div
      class="tab-row ${this._layoutTier === "narrow" ? "narrow" : ""}"
      role="tablist"
      aria-label="Tables"
      @keydown=${(e) => this._onTabKeydown(e)}
    >
      ${H.map((e) => {
			let r = e === this._activeTab;
			return v`<button
          type="button"
          role="tab"
          class="tab-btn ${D("tab-label")}"
          id="tab-${e}"
          aria-controls="tabpanel"
          aria-label=${ir(e, n[e], t.filtering ? t.counts[e] : null)}
          aria-selected=${r ? "true" : "false"}
          tabindex=${r ? "0" : "-1"}
          @click=${() => this._selectTab(e)}
        ><span class="tab-name">${tr[e]}</span> <span class="tab-count">(${n[e]})</span>${t.filtering ? v` <span class="tab-match ${O("small-text")}">${rr(t.counts[e])}</span>` : ""}</button>`;
		})}
    </div>`;
	}
	_selectTab(e) {
		this._activeTab = e, Ti(e);
	}
	_onTabKeydown(e) {
		let t = ar(this._activeTab, e.key);
		t !== null && (e.preventDefault(), this._selectTab(t), this.updateComplete.then(() => this.renderRoot.querySelector(`#tab-${t}`)?.focus()));
	}
	_renderStructuredView(e, t, n, r) {
		if (this._layoutTier === "wide") return v`
        <div class="panes">
          <div class="pane pane-side">${this._renderApplianceCards(e, t, n, r)}</div>
          <div class="pane pane-main">${this._renderCoTable(e, t, n, r)}</div>
          <div class="pane pane-side">${this._renderUoCards(e, t, n, r)}</div>
        </div>
      `;
		let i = this._activeTab === "devices" ? this._layoutTier === "narrow" ? this._renderCoCards(e, t, n, r) : this._renderCoTable(e, t, n, r) : this._activeTab === "appliances" ? this._renderApplianceCards(e, t, n, r) : this._renderUoCards(e, t, n, r);
		return v`
      <div class="panes">
        <div class="pane pane-single" id="tabpanel" role="tabpanel" aria-labelledby="tab-${this._activeTab}">
          ${i}
        </div>
      </div>
    `;
	}
	_renderCardBand(e, t, n, r, i, a) {
		let o = i ? n.filter(a) : n;
		if (i && o.length === 0) return "";
		let s = !i && this._collapsedCardBandGroups[e].has(t);
		return v`
      <div class="card-section-header section-${t === "isolated" ? "isolated" : "in-use"}" role="group" aria-label="${_i[t]}">
        ${this._renderCardBandGroupToggle(e, t, n.length, i)}
      </div>
      ${s ? "" : o.length === 0 ? v`<div class="card-none ${Z}">— none —</div>` : o.map(r)}
    `;
	}
	_renderNoMainMatch(e, t) {
		return e && !t ? v`<p class="no-filter-match ${O("supporting-text")}">${Fn}</p>` : "";
	}
	_renderApplianceCards(e, t, n, r) {
		let { isolated: i, inUse: a } = ui(e), o = (e) => r.appliances.has(e.appliance_id), s = this._plainTip("New Appliance"), c = (e, r) => {
			let i = n.appliance.get(e.appliance_id), a = Ri(e, t), o = _a(e, t);
			return v`<div
        class="entity-card appliance-card ${r ? Z : ""} ${i ? "pending" : ""}"
        role="group"
        aria-label=${e.name}
      >
        <div class="card-line card-identity">
          ${this._renderDeleteButton({
				kind: "appliance",
				entity: e
			})}
          ${this._renderNameLink({
				kind: "appliance",
				entity: e
			}, e.name)}
        </div>
        <div class="card-line appliance-connection">
          ${a === null || o === null ? "" : v`<span class="connection-host">${"in"}
                  ${this._renderNameLink(a.kind === "co_socket" ? {
				kind: "co",
				entity: a.co
			} : {
				kind: "uo",
				entity: a.uo
			}, o.name)}
                  ${o.suffix ?? ""}</span>`}
          ${i ? this._renderPendingMarker(this._pendingMarkerText(i, t)) : ""}
          ${this._renderLinkButton({
				kind: "appliance",
				entity: e
			}, t)}
        </div>
      </div>`;
		};
		return v`
      <div class="card-header">
        <button class="create-btn ${O("small-text", "emphasis")}" data-tip="act" aria-describedby=${s.id} @click=${() => this._openCreate("appliance")}>
          Add Appliance
        </button>${s.desc}
      </div>
      <div class="entity-cards appliance-cards">
        ${this._renderCardBand("appliance", "isolated", i, (e) => c(e, !0), r.filtering, o)}
        ${this._renderCardBand("appliance", "in_use", a, (e) => c(e, !1), r.filtering, o)}
        ${this._renderNoMainMatch(r.filtering, r.appliances.size > 0)}
      </div>
    `;
	}
	_renderUoCards(e, t, n, r) {
		let { isolated: i, inUse: a } = di(e), o = (e) => r.uos.has(e.uo_id), s = this._plainTip("New Wall Socket"), c = (e, r) => {
			let i = n.uo.get(e.uo_id), a = zi(e, t), o = Bi(e, t);
			return v`<div
        class="entity-card uo-card ${r ? Z : ""} ${i ? "pending" : ""}"
        role="group"
        aria-label=${e.name}
      >
        <div class="card-line card-identity">
          <div class="entity-flank-content">
            ${this._renderDeleteButton({
				kind: "uo",
				entity: e
			})}
            ${this._renderNameLink({
				kind: "uo",
				entity: e
			}, e.name)}
            ${this._renderAttrList(sa(e, this._uoArea(e)))}
          </div>
        </div>
        <div class="card-line uo-connection">
          ${i ? this._renderPendingMarker(this._pendingMarkerText(i, t)) : ""}
          ${this._renderLinkButton({
				kind: "uo",
				entity: e
			}, t)}
          ${a.length > 0 ? v`<span class="uo-occupants">${ia}
                  <span class="uo-occupant-list">${a.map((e) => v`<div>${this._renderNameLink({
				kind: "co",
				entity: e
			}, e.alias)}</div>`)}</span></span>` : ""}
          ${o.length > 0 ? v`<span class="uo-occupants">${aa}
                  <span class="uo-occupant-list">${o.map((e) => v`<div>${this._renderNameLink({
				kind: "appliance",
				entity: e
			}, e.name)}</div>`)}</span></span>` : ""}
        </div>
      </div>`;
		};
		return v`
      <div class="card-header">
        <button class="create-btn ${O("small-text", "emphasis")}" data-tip="act" aria-describedby=${s.id} @click=${() => this._openCreate("uo")}>
          Add Wall Socket
        </button>${s.desc}
      </div>
      <div class="entity-cards uo-cards">
        ${this._renderCardBand("uo", "isolated", i, (e) => c(e, !0), r.filtering, o)}
        ${this._renderCardBand("uo", "in_use", a, (e) => c(e, !1), r.filtering, o)}
        ${this._renderNoMainMatch(r.filtering, r.uos.size > 0)}
      </div>
    `;
	}
	_renderDeviceInfo(e) {
		let t = this._coDevice(e);
		return v`<div class="card-name">
      ${this._renderDeleteButton({
			kind: "co",
			entity: e
		})}
      ${this._renderNameLink({
			kind: "co",
			entity: e
		}, e.alias)}${this._maybeNewBadge(e.co_id)}
      <span class="card-model ${D("dialog-field-note")}">${la(t, "cards")}</span>
    </div>`;
	}
	_coNameHover(e) {
		let t = this._coDevice(e), n = this._helpers(), r = this._areas.names;
		return Ni({
			name: e.alias,
			integration: qn(this.hass?.entities, e.co_id),
			model: t.model,
			uoName: n ? Ai(e, n) : null,
			effectiveArea: e.effective_ha_area_id ? M(r, e.effective_ha_area_id) : null,
			deviceArea: t.area_id ? M(r, t.area_id) : null
		});
	}
	_renderCoBox(e, t) {
		let n = this._coDevice(e), r = Di(e, t);
		return v`<div class="co-box">
      <div class="co-box-identity">
        ${this._debugMode ? v`<div class="co-box-delete">${this._renderDeleteButton({
			kind: "co",
			entity: e
		})}</div>` : ""}
        <div class="co-box-name ${O("medium")}">
          ${this._renderNameLink({
			kind: "co",
			entity: e
		}, e.alias)}${this._maybeNewBadge(e.co_id)}
        </div>
        <div class="co-box-model ${D("dialog-field-note")}">${la(n, "table")}</div>
      </div>
      ${r === null ? "" : v`<div class="co-box-plugged ${D("dialog-field-note")}">${r}</div>`}
    </div>`;
	}
	_renderCoCards(e, t, n, r) {
		let i = Vi(t), a = Ui(e, t), o = r.filtering;
		return v`<div class="entity-cards co-cards">
      ${ml.map((e) => {
			let s = i[e].map((t, n) => ({
				block: t,
				key: ga(e, n)
			})).filter(({ key: e }) => !o || r.blocks.has(e));
			return s.length === 0 ? "" : this._renderCoCardSection(e, s, a[e], o, t, n);
		})}
      ${this._renderNoMainMatch(o, r.blocks.size > 0)}
    </div>`;
	}
	_renderCoCardSection(e, t, n, r, i, a) {
		let o = !r && this._collapsedSections.has(e);
		return v`
      <div class="card-section-header section-${e}" role="group" aria-label="${fi[e]}">
        ${this._renderSectionCollapseToggle(e, n, r)}
      </div>
      ${o ? "" : t.map(({ block: e, key: t }) => {
			let n = e.uoId === null ? null : i.uosById.get(e.uoId) ?? null;
			return e.rows.map((e) => this._renderCoCardRow(e, n, t, i, a));
		})}
    `;
	}
	_renderCoCardRow(e, t, n, r, i) {
		switch (e.kind) {
			case "live": return this._renderCoCard(e.co, t, n, r, i);
			case "copy": return "";
			case "direct": return this._renderCoDirectCard(e.appliance, t, n, r);
		}
	}
	_renderCoCardSocketLine(e, t, n, r) {
		let { appliance: i, co: a, name: o } = Ei(t, n), s = r.coSocket.get(t.co_socket_id);
		return v`<div class="card-line socket-line ${n.socketIsFullyChained(e, t) ? "" : Z}">
      ${this._renderSocketLinkButton(t, i, n)}
      ${this._renderSocketIdentity(t)}
      ${s ? this._renderPendingMarker(this._pendingMarkerText(s, n)) : ""}
      ${this._renderOccupantName(i, a, o)}${this._renderDepartingName(t, r, n)}
    </div>`;
	}
	_renderCoCard(e, t, n, r, i) {
		let a = r.socketsByCo.get(e.co_id) ?? [], o = i.co.get(e.co_id), s = !r.coIsFullyChained(e), c = t === null || !r.uoIsFullyChained(t), l = Oi(e, r), u = l === null ? null : ki(e, r);
		return v`<div
      class="entity-card co-card ${s ? Z : ""} ${o ? "pending" : ""}"
      role="group"
      aria-label=${e.alias}
      data-block=${n}
    >
      <div class="card-identity">${this._renderDeviceInfo(e)}</div>
      ${a.map((t) => this._renderCoCardSocketLine(e, t, r, i))}
      <div class="card-line uo-line ${c ? Z : ""}">
        ${l === null ? t ? this._renderCoCardUoText(t) : "" : v`<span class="entity-flank-content uo-text host-text"><span class="host-name">${l}</span>${u === null ? "" : v`<span class="power-source ${D("dialog-field-note")}">${u}</span>`}</span>`}
        ${o ? this._renderPendingMarker(this._pendingMarkerText(o, r)) : ""}
        ${this._renderLinkButton({
			kind: "co",
			entity: e
		}, r)}
      </div>
    </div>`;
	}
	_renderCoCardUoText(e) {
		return v`<span class="entity-flank-content uo-text">
      ${this._renderUoIdentity(e)}
    </span>`;
	}
	_renderCoDirectCard(e, t, n, r) {
		return v`<div
      class="entity-card co-card direct-card"
      role="group"
      aria-label=${e.name}
      data-block=${n}
    >
      <div class="card-line">
        ${this._renderNameLink({
			kind: "appliance",
			entity: e
		}, e.name)}
        ${this._renderLinkButton({
			kind: "appliance",
			entity: e
		}, r)}
      </div>
      <div class="card-line uo-line">
        ${t ? this._renderCoCardUoText(t) : ""}
      </div>
    </div>`;
	}
	_renderCoTable(e, t, n, r) {
		let i = Vi(t), a = Ui(e, t), o = {
			h: t,
			pending: n,
			matches: r,
			sectionCounts: a,
			nextShade: Cc()
		};
		return v`
      <table class="structured-table co-table">
        ${this._renderCoTableHead({
			appliances: e.appliances.length,
			cos: e.cos.length,
			...bc(a),
			uos: e.uos.length
		})} ${Sc(ml, i, r).map((e) => this._renderCoSection(e, o))}
      </table>
      ${this._renderNoMainMatch(r.filtering, r.blocks.size > 0)}
    `;
	}
	_renderCoTableHead(e) {
		let t = this._tip(Qi("appliance", e)), n = this._tip(Qi("co", e)), r = this._tip(Qi("uo", e)), i = v`${this._renderPowerIcon(Wc, "Plug", "plug")}${this._renderPowerIcon(qc, "Unplug", "unplug")}`;
		return v`<thead>
          <tr>
            <th class="th-appliance ${D("column-heading")}">
              <div class="th-stack">
                <span class="th-content section-count-tooltip" tabindex="0" data-tip="info" aria-describedby=${t.id}>Appliances<sup class="info-cue ${D("info-cue")}" aria-hidden="true">i</sup></span>${t.desc}
              </div>
            </th>
            <th class="th-connection ${D("column-heading")}"><div class="th-row">${i}</div></th>
            <th class="th-co ${D("column-heading")}" colspan="2">
              <div class="th-stack">
                <span class="th-content section-count-tooltip" tabindex="0" data-tip="info" aria-describedby=${n.id}>Smart devices &amp; Sockets<sup class="info-cue ${D("info-cue")}" aria-hidden="true">i</sup></span>${n.desc}
              </div>
            </th>
            <th class="th-connection ${D("column-heading")}"><div class="th-row">${i}</div></th>
            <th class="th-uo ${D("column-heading")}">
              <div class="th-stack">
                <span class="th-content section-count-tooltip" tabindex="0" data-tip="info" aria-describedby=${r.id}>Wall Sockets<sup class="info-cue ${D("info-cue")}" aria-hidden="true">i</sup></span>${r.desc}
              </div>
            </th>
          </tr>
        </thead>`;
	}
	_renderCoSection({ section: e, blocks: t, headed: n, spacerBefore: r }, i) {
		let { matches: a, sectionCounts: o } = i;
		return v`
      ${r ? v`<tbody>
                  ${fl(dl)}
                </tbody>` : ""}
      ${n ? v`<tbody>
                <tr class="section-header section-${e}" aria-label="${fi[e]}">
                  <td colspan="${dl}">
                    ${this._renderSectionCollapseToggle(e, o[e], a.filtering)}
                  </td>
                </tr>
              </tbody>` : ""}
      ${t.map((t, n) => {
			let r = ga(e, n), o = xc(a, this._collapsedSections, e, r);
			return v`${pl(o)}${this._renderCoBlock(t, r, o, i)}`;
		})}
    `;
	}
	_renderCoBlock(e, t, n, r) {
		let { h: i, pending: a } = r, o = yc(i.socketsByCo, e), s = e.uoId === null ? null : i.uosById.get(e.uoId) ?? null, c = s === null || !i.uoIsFullyChained(s), l = r.nextShade(), u = !1, d = () => u ? "" : (u = !0, v`<td rowspan="${o}" class="uo-cell ${c ? Z : ""}">
          ${s ? v`<div class="entity-flank-content">
                ${this._renderUoIdentity(s)}
              </div>` : ""}
        </td>`), f = e.rows.flatMap((e) => [...e.gapBefore ? [fl(5)] : [], ...this._renderCoRows(e, d, i, a)]);
		return v`<tbody class="${l} ${n ? "collapsed" : ""}" ?inert=${n} data-block=${t}>${f}</tbody>`;
	}
	_renderCoRows(e, t, n, r) {
		switch (e.kind) {
			case "live": return this._renderLiveRows(e.co, t, n, r);
			case "copy": return this._renderCopyRows(e.co, e.sockets, t, n);
			case "direct": return [this._renderDirectRow(e.appliance, t, n)];
		}
	}
	_renderLiveRows(e, t, n, r) {
		let i = [], a = n.socketsByCo.get(e.co_id) ?? [], o = !n.coIsFullyChained(e), s = _c(n.socketsByCo, e), c = r.co.get(e.co_id), l = v`<td
      rowspan="${s}"
      class="connection-cell co-connection"
    >
      <span class="connection-leader before"></span>${this._renderLinkButton({
			kind: "co",
			entity: e
		}, n)}${c ? this._renderPendingMarker(this._pendingMarkerText(c, n)) : ""}
    </td>`, u = t(), d = (e, t, i) => {
			let a = e.occupant_device_id !== null, { appliance: o, co: s, name: c } = Ei(e, n);
			return v`<td
          class="appl-cell ${a ? `plugged ${O("emphasis")}` : ""} ${t ? Z : ""}"
        >
          ${i ? this._renderPendingMarker(this._pendingMarkerText(i, n)) : ""}
          ${this._renderOccupantName(o, s, c)}${this._renderDepartingName(e, r, n)}
        </td>
        <td class="connection-cell socket-connection">
          ${this._renderSocketLinkButton(e, o, n)}<span class="connection-leader after"></span>
        </td>`;
		}, f = this._renderCoBox(e, n);
		return a.length === 0 ? (i.push(v`
        <tr class="${c ? "pending" : ""}">
          <td class="appl-cell"></td>
          <td class="connection-cell"></td>
          <td colspan="2" class="co-cell co-box-left co-box-right co-box-top co-box-bottom ${o ? Z : ""}">
            ${f}
          </td>
          ${l}
          ${u}
        </tr>
      `), i) : (a.forEach((t, s) => {
			let ee = !n.socketIsFullyChained(e, t), te = r.coSocket.get(t.co_socket_id), p = s === 0, ne = s === a.length - 1;
			i.push(v`
        <tr class="socket-row ${p && c || te ? "pending" : ""}">
          ${d(t, ee, te)}
          <td class="socket-cell co-box-left ${p ? "co-box-top" : ""} ${ne ? "co-box-bottom" : ""} ${ee ? Z : ""}">
            <div class="entity-flank-content">
              ${this._renderSocketIdentity(t)}
            </div>
          </td>
          ${p ? v`<td
                  rowspan="${a.length}"
                  class="co-cell co-box-right co-box-top co-box-bottom ${o ? Z : ""}"
                >
                  ${f}
                </td>` : ""}
          ${p ? l : ""}
          ${p ? u : ""}
        </tr>
      `);
		}), i);
	}
	_renderCopyRows(e, t, n, r) {
		let i = n();
		return t.map((n, a) => {
			let o = a === 0, s = a === t.length - 1;
			return v`
        <tr class="socket-row copy-row">
          <td class="appl-cell" inert></td>
          <td class="connection-cell socket-connection" inert>
            ${this._renderHostingMark()}<span class="connection-leader after"></span>
          </td>
          <td class="socket-cell co-box-left ${o ? "co-box-top" : ""} ${s ? "co-box-bottom" : ""}" inert>
            <div class="entity-flank-content">${this._renderSocketIdentity(n)}</div>
          </td>
          ${o ? v`<td
                  rowspan="${t.length}"
                  class="co-cell copy-cell co-box-right co-box-top co-box-bottom"
                  inert
                >
                  <div class="co-alias ${O("medium")}">${Ii(e, t, r)}</div>
                </td>` : ""}
          ${o ? v`<td rowspan="${t.length}" class="connection-cell co-connection" inert></td>` : ""}
          ${o ? i : ""}
        </tr>
      `;
		});
	}
	_renderDirectRow(e, t, n) {
		return v`
      <tr class="direct-row">
        <td class="appl-cell plugged">
          ${this._renderNameLink({
			kind: "appliance",
			entity: e
		}, e.name)}
        </td>
        <td class="connection-cell socket-connection">
          ${this._renderLinkButton({
			kind: "appliance",
			entity: e
		}, n)}<span class="connection-leader after"></span>
        </td>
        <td colspan="2" class="direct-line-cell"><div class="direct-line"></div></td>
        <td class="connection-cell co-connection"><span class="connection-leader before"></span></td>
        ${t()}
      </tr>
    `;
	}
};
X([qe({ attribute: !1 })], $.prototype, "hass", void 0), X([S()], $.prototype, "_state", void 0), X([S()], $.prototype, "_editSession", void 0), X([S()], $.prototype, "_debugMode", void 0), X([S()], $.prototype, "_build", void 0), X([S()], $.prototype, "_error", void 0), X([S()], $.prototype, "_loading", void 0), X([S()], $.prototype, "_socketRegion", void 0), X([S()], $.prototype, "_haItems", void 0), X([S()], $.prototype, "_mode", void 0), X([S()], $.prototype, "_themeOverride", void 0), X([S()], $.prototype, "_collapsedSections", void 0), X([S()], $.prototype, "_collapsedCardBandGroups", void 0), X([S()], $.prototype, "_layoutTier", void 0), X([S()], $.prototype, "_activeTab", void 0), X([S()], $.prototype, "_editing", void 0), X([S()], $.prototype, "_editingSocket", void 0), X([S()], $.prototype, "_linking", void 0), X([S()], $.prototype, "_linkRoomFilter", void 0), X([S()], $.prototype, "_linkCoFilter", void 0), X([S()], $.prototype, "_creating", void 0), X([S()], $.prototype, "_deleting", void 0), X([S()], $.prototype, "_flushConfirm", void 0), X([S()], $.prototype, "_commitConfirm", void 0), X([S()], $.prototype, "_settingsOpen", void 0), X([S()], $.prototype, "_menuOpen", void 0), X([S()], $.prototype, "_mainFilter", void 0), X([S()], $.prototype, "_filterOpen", void 0), X([S()], $.prototype, "_filterPos", void 0), X([S()], $.prototype, "_fromNames", void 0), X([S()], $.prototype, "_exporting", void 0), X([S()], $.prototype, "_wallBatch", void 0), X([S()], $.prototype, "_discovered", void 0), X([C("dialog.edit-dialog")], $.prototype, "_dialogEl", void 0), X([C("dialog.socket-edit-dialog")], $.prototype, "_socketDialogEl", void 0), X([C("dialog.link-dialog")], $.prototype, "_linkDialogEl", void 0), X([C("dialog.create-dialog")], $.prototype, "_createDialogEl", void 0), X([C("dialog.delete-dialog")], $.prototype, "_deleteDialogEl", void 0), X([C("dialog.flush-dialog")], $.prototype, "_flushDialogEl", void 0), X([C("dialog.commit-dialog")], $.prototype, "_commitDialogEl", void 0), X([C("dialog.settings-dialog")], $.prototype, "_settingsDialogEl", void 0), X([C("dialog.ha-items-dialog")], $.prototype, "_haItemsDialogEl", void 0), X([C("dialog.from-names-dialog")], $.prototype, "_fromNamesDialogEl", void 0), X([C("dialog.export-dialog")], $.prototype, "_exportDialogEl", void 0), X([C("dialog.wall-batch-dialog")], $.prototype, "_wallBatchDialogEl", void 0), X([C("dialog.discovered-dialog")], $.prototype, "_discoveredDialogEl", void 0), X([C("input.main-filter-input")], $.prototype, "_mainFilterInputEl", void 0), X([C("button.main-filter-open")], $.prototype, "_mainFilterOpenEl", void 0), X([C("#main-filter")], $.prototype, "_mainFilterEl", void 0), X([C(".tooltip-popover")], $.prototype, "_popoverEl", void 0), X([C(".menu-btn")], $.prototype, "_menuBtnEl", void 0), $ = X([We("outlet-binder-panel")], $);
//#endregion
export { $ as OutletBinderPanel };
