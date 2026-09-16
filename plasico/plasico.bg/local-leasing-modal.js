(function () {
	var CART_STORAGE_KEY = 'plasico-hss2026-cart';

	/**
	 * Left: personal finance / „Купи на изплащане“ (BNP-style multipliers).
	 * Right: PostBank credit-card installments (distinct, slightly lower rates).
	 * Rates/fees are client-side approximations for local preview only.
	 */
	var COLUMNS = {
		personal: {
			id: 'personal',
			provider: 'bnp',
			title: 'Купи на изплащане',
			terms: [
				{ months: 3, multiplier: 1.185, glp: 17.91, gpr: 19.4, fee: 0 },
				{ months: 6, multiplier: 1.235, glp: 17.91, gpr: 19.4, fee: 0 },
				{ months: 12, multiplier: 1.29, glp: 17.91, gpr: 19.4, fee: 0 },
			],
		},
		postbank: {
			id: 'postbank',
			provider: 'postbank',
			title: 'Купи на вноски с кредитна карта на PostBank',
			terms: [
				{ months: 3, multiplier: 1.178, glp: 14.34, gpr: 15.29, fee: 0 },
				{ months: 6, multiplier: 1.221, glp: 14.34, gpr: 15.29, fee: 0 },
				{ months: 9, multiplier: 1.234, glp: 14.34, gpr: 15.29, fee: 0 },
				{ months: 12, multiplier: 1.261, glp: 14.34, gpr: 15.29, fee: 0 },
			],
		},
	};

	var MONTH_ROWS = [3, 6, 9, 12];
	var DEFAULT_PERSONAL_MONTHS = 12;

	var state = {
		column: 'personal',
		selectedMonths: DEFAULT_PERSONAL_MONTHS,
		personalMonths: DEFAULT_PERSONAL_MONTHS,
		price: 0,
		downPayment: 0,
		promoCode: '',
		prodId: '',
	};

	function formatEuro(amount) {
		return amount.toFixed(2).replace('.', ',') + ' €';
	}

	function formatPercent(value) {
		return value.toFixed(2).replace('.', ',') + '%';
	}

	function parseEuroText(text) {
		if (!text) return 0;
		var normalized = String(text)
			.replace(/\u00a0/g, ' ')
			.replace(/\s+/g, ' ')
			.trim();
		var match = normalized.match(/(\d[\d\s]*)([.,])(\d{2})/);
		if (!match) return 0;
		var whole = match[1].replace(/\s/g, '');
		return parseFloat(whole + '.' + match[3]) || 0;
	}

	function parseLooseAmount(text) {
		if (text == null || text === '') return 0;
		var normalized = String(text)
			.replace(/\u00a0/g, ' ')
			.replace(/\s+/g, '')
			.replace(',', '.')
			.replace(/[^\d.-]/g, '');
		var value = parseFloat(normalized);
		return isFinite(value) && value > 0 ? value : 0;
	}

	function readCartFromStorage() {
		try {
			var raw = localStorage.getItem(CART_STORAGE_KEY);
			var parsed = raw ? JSON.parse(raw) : [];
			return Array.isArray(parsed) ? parsed : [];
		} catch (e) {
			return [];
		}
	}

	function getCartSubtotal(items) {
		return items.reduce(function (sum, item) {
			return sum + (Number(item.price) || 0) * (Number(item.qty) || 0);
		}, 0);
	}

	function parsePriceFromDom() {
		var selectors = [
			'#cart-drawer-subtotal',
			'.js-summary-products',
			'.js-summary-total',
		];

		for (var i = 0; i < selectors.length; i++) {
			var el = document.querySelector(selectors[i]);
			if (!el) continue;
			var amount = parseEuroText(el.textContent);
			if (amount > 0) return amount;
		}

		return 0;
	}

	function parsePrice() {
		var fromStorage = getCartSubtotal(readCartFromStorage());
		if (fromStorage > 0) return fromStorage;
		return parsePriceFromDom();
	}

	function getProdId() {
		var input = document.querySelector('#buy-form input[name="prod_id"]');
		return input ? input.value : '';
	}

	function getFinancedAmount() {
		var financed = state.price - (Number(state.downPayment) || 0);
		return financed > 0 ? financed : 0;
	}

	function calcTerm(price, term) {
		var total = price * term.multiplier;
		var monthly = term.months > 0 ? total / term.months : 0;
		return {
			months: term.months,
			monthly: monthly,
			total: total,
			glp: term.glp,
			gpr: term.gpr,
			fee: term.fee || 0,
			multiplier: term.multiplier,
		};
	}

	function findColumnTerm(columnId, months) {
		var column = COLUMNS[columnId];
		if (!column) return null;
		for (var i = 0; i < column.terms.length; i++) {
			if (column.terms[i].months === months) {
				return calcTerm(getFinancedAmount(), column.terms[i]);
			}
		}
		return null;
	}

	function ensurePersonalMonthsValid() {
		if (findColumnTerm('personal', state.personalMonths)) return;
		if (findColumnTerm('personal', DEFAULT_PERSONAL_MONTHS)) {
			state.personalMonths = DEFAULT_PERSONAL_MONTHS;
			return;
		}
		state.personalMonths = COLUMNS.personal.terms[COLUMNS.personal.terms.length - 1].months;
	}

	function ensureSelectionValid() {
		if (findColumnTerm(state.column, state.selectedMonths)) return;
		var terms = COLUMNS[state.column].terms;
		state.selectedMonths = terms[terms.length - 1].months;
	}

	function getSelectedTerm() {
		var term = findColumnTerm(state.column, state.selectedMonths);
		if (term) return term;
		var fallbackColumn = COLUMNS[state.column] || COLUMNS.personal;
		var last = fallbackColumn.terms[fallbackColumn.terms.length - 1];
		return calcTerm(getFinancedAmount(), last);
	}

	/** Teaser always reflects left-column „изплащане“ (not credit-card). */
	function getTeaserTerm() {
		ensurePersonalMonthsValid();
		var term = findColumnTerm('personal', state.personalMonths);
		if (term) return term;
		var last = COLUMNS.personal.terms[COLUMNS.personal.terms.length - 1];
		return calcTerm(getFinancedAmount(), last);
	}

	function teaserText(term) {
		return 'За ' + term.months + ' месеца x ' + formatEuro(term.monthly);
	}

	function summaryText(term) {
		return formatEuro(term.monthly) + ' / месец - ' + term.months + ' вноски';
	}

	function schemeCardHtml(columnId, term) {
		if (!term) {
			return '<div class="pl-leasing-cell pl-leasing-cell--empty" aria-hidden="true"></div>';
		}

		var isActive =
			state.column === columnId && state.selectedMonths === term.months;
		var radioId = 'pl-leasing-' + columnId + '-' + term.months;

		return (
			'<label class="pl-leasing-cell' +
			(isActive ? ' is-active' : '') +
			'" for="' +
			radioId +
			'" data-column="' +
			columnId +
			'">' +
			'<input' +
			' type="radio"' +
			' class="pl-leasing-radio"' +
			' name="pl-leasing-scheme"' +
			' id="' +
			radioId +
			'"' +
			' data-column="' +
			columnId +
			'"' +
			' data-months="' +
			term.months +
			'"' +
			(isActive ? ' checked' : '') +
			' />' +
			'<span class="pl-leasing-cell-body">' +
			'<span class="pl-leasing-cell-months">' +
			term.months +
			' месеца</span>' +
			'<span class="pl-leasing-cell-monthly">' +
			formatEuro(term.monthly) +
			'</span>' +
			'<span class="pl-leasing-cell-meta">' +
			'ГЛП: ' +
			formatPercent(term.glp) +
			'<br />' +
			'ГПР: ' +
			formatPercent(term.gpr) +
			'<br />' +
			'Такса ангажимент: ' +
			formatEuro(term.fee) +
			'<br />' +
			'Общо: ' +
			formatEuro(term.total) +
			'</span>' +
			'</span>' +
			'</label>'
		);
	}

	function ensureModal() {
		if (document.getElementById('pl-leasing-overlay')) {
			return document.getElementById('pl-leasing-overlay');
		}

		var overlay = document.createElement('div');
		overlay.id = 'pl-leasing-overlay';
		overlay.className = 'pl-leasing-overlay';
		overlay.hidden = true;
		overlay.innerHTML =
			'<div class="pl-leasing-modal" role="dialog" aria-modal="true" aria-labelledby="pl-leasing-title">' +
			'  <button type="button" class="pl-leasing-close" aria-label="Затвори">&times;</button>' +
			'  <div class="pl-leasing-head">' +
			'    <div class="pl-leasing-title-wrap">' +
			'      <h2 class="pl-leasing-title" id="pl-leasing-title">Купи на изплащане</h2>' +
			'      <p class="pl-leasing-subtitle">Сравни схемите и избери удобен план за плащане</p>' +
			'    </div>' +
			'  </div>' +
			'  <div class="pl-leasing-body">' +
			'    <div class="pl-leasing-toolbar">' +
			'      <label class="pl-leasing-field">' +
			'        <span class="pl-leasing-field-label">Промо код:</span>' +
			'        <input type="text" id="pl-leasing-promo" class="pl-leasing-input" placeholder="Промо код..." autocomplete="off" />' +
			'      </label>' +
			'      <label class="pl-leasing-field">' +
			'        <span class="pl-leasing-field-label">Първоначална вноска:</span>' +
			'        <input type="text" id="pl-leasing-down" class="pl-leasing-input" inputmode="decimal" />' +
			'      </label>' +
			'      <button type="button" class="pl-leasing-recalc" id="pl-leasing-recalc">Преизчисли</button>' +
			'    </div>' +
			'    <div class="pl-leasing-summary" id="pl-leasing-summary"></div>' +
			'    <div class="pl-leasing-grid-wrap">' +
			'      <div class="pl-leasing-grid" id="pl-leasing-grid" role="table" aria-label="Схеми на изплащане"></div>' +
			'    </div>' +
			'    <form class="pl-leasing-apply" id="pl-leasing-apply" novalidate>' +
			'      <h3 class="pl-leasing-apply-title">Кандидатствай за лизинг:</h3>' +
			'      <div class="pl-leasing-apply-fields">' +
			'        <input type="text" name="full_name" id="pl-leasing-name" class="pl-leasing-apply-input" placeholder="Име и фамилия... (задължително на кирилица)" autocomplete="name" />' +
			'        <input type="tel" name="phone" id="pl-leasing-phone" class="pl-leasing-apply-input" placeholder="Телефон за контакти... (започващ с нула)" autocomplete="tel" inputmode="tel" />' +
			'        <input type="text" name="egn" id="pl-leasing-egn" class="pl-leasing-apply-input" placeholder="ЕГН..." autocomplete="off" inputmode="numeric" />' +
			'        <input type="email" name="email" id="pl-leasing-email" class="pl-leasing-apply-input" placeholder="Ел. поща..." autocomplete="email" />' +
			'      </div>' +
			'      <p class="pl-leasing-apply-help">Моля въведете коректна ел. поща. На нея ще получите инструкции за завършване на Вашата кандидатура за кредитиране.</p>' +
			'      <div class="pl-leasing-apply-checks">' +
			'        <label class="pl-leasing-apply-check">' +
			'          <input type="checkbox" name="agree_terms" id="pl-leasing-agree-terms" value="1" />' +
			'          <span>Имам навършени 18 години и съм съгласен с <a class="pl-leasing-apply-link" href="https://plasico.bg/help?info=52" target="_blank" rel="noopener noreferrer">общите условия и начина на обработка на личните ми данни</a></span>' +
			'        </label>' +
			'        <label class="pl-leasing-apply-check">' +
			'          <input type="checkbox" name="agree_apply" id="pl-leasing-agree-apply" value="1" />' +
			'          <span>Запознах се с <a class="pl-leasing-apply-link" href="https://plasico.bg/help?info=52" target="_blank" rel="noopener noreferrer">условията за кандидатстване на ПБ Лични финанси</a></span>' +
			'        </label>' +
			'        <label class="pl-leasing-apply-check">' +
			'          <input type="checkbox" name="agree_privacy" id="pl-leasing-agree-privacy" value="1" />' +
			'          <span>Запознах се с <a class="pl-leasing-apply-link" href="https://static.plasico.bg/resources/191112164954personal_data_policy.pdf" target="_blank" rel="noopener noreferrer">информацията за защита на личните данни</a></span>' +
			'        </label>' +
			'      </div>' +
			'      <a class="pl-leasing-apply-product" href="http://dw-file.eu/%D0%91%D0%9D%D0%9F%20%D0%9F%D0%B0%D1%80%D0%B8%D0%B1%D0%B0%20%D0%9B%D0%A4-%D0%9F%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D0%BE%D0%B2%D0%B0%20%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%86%D0%B8%D1%8F.pdf" target="_blank" rel="noopener noreferrer">Продуктова Информация на ПБ Лични финанси</a>' +
			'      <p class="pl-leasing-apply-error" id="pl-leasing-apply-error" hidden></p>' +
			'      <p class="pl-leasing-apply-success" id="pl-leasing-apply-success" hidden></p>' +
			'      <button type="submit" class="pl-leasing-apply-submit" id="pl-leasing-apply-submit">Кандидатствай онлайн</button>' +
			'    </form>' +
			'  </div>' +
			'</div>';

		document.body.appendChild(overlay);

		overlay.addEventListener('click', function (e) {
			if (e.target === overlay) closeModal();
		});

		overlay.querySelector('.pl-leasing-close').addEventListener('click', closeModal);

		overlay.querySelector('#pl-leasing-recalc').addEventListener('click', function () {
			applyToolbarInputs();
			renderModal();
			renderTeaser();
		});

		['#pl-leasing-down', '#pl-leasing-promo'].forEach(function (sel) {
			overlay.querySelector(sel).addEventListener('keydown', function (e) {
				if (e.key === 'Enter') {
					e.preventDefault();
					applyToolbarInputs();
					renderModal();
					renderTeaser();
				}
			});
		});

		overlay.querySelector('#pl-leasing-apply').addEventListener('submit', handleApplySubmit);

		document.addEventListener('keydown', function (e) {
			if (e.key === 'Escape' && !overlay.hidden) {
				closeModal();
			}
		});

		return overlay;
	}

	function isCyrillicName(value) {
		var trimmed = String(value || '').trim();
		if (!trimmed) return false;
		return /^[\u0400-\u04FF\s\-'.]+$/.test(trimmed) && /[\u0400-\u04FF]/.test(trimmed);
	}

	function isPhoneStartingWithZero(value) {
		var digits = String(value || '').replace(/[\s\-()]/g, '');
		return /^0\d{8,9}$/.test(digits);
	}

	function isLikelyEgn(value) {
		var digits = String(value || '').replace(/\s+/g, '');
		return /^\d{10}$/.test(digits);
	}

	function isEmailFormat(value) {
		var trimmed = String(value || '').trim();
		return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed);
	}

	function clearApplyFeedback() {
		var errorEl = document.getElementById('pl-leasing-apply-error');
		var successEl = document.getElementById('pl-leasing-apply-success');
		if (errorEl) {
			errorEl.hidden = true;
			errorEl.textContent = '';
		}
		if (successEl) {
			successEl.hidden = true;
			successEl.textContent = '';
		}
		Array.prototype.slice
			.call(document.querySelectorAll('.pl-leasing-apply-input.is-invalid, .pl-leasing-apply-check.is-invalid'))
			.forEach(function (el) {
				el.classList.remove('is-invalid');
			});
	}

	function showApplyError(message) {
		var errorEl = document.getElementById('pl-leasing-apply-error');
		var successEl = document.getElementById('pl-leasing-apply-success');
		if (successEl) {
			successEl.hidden = true;
			successEl.textContent = '';
		}
		if (!errorEl) return;
		errorEl.hidden = false;
		errorEl.textContent = message;
	}

	function showApplySuccess(message) {
		var errorEl = document.getElementById('pl-leasing-apply-error');
		var successEl = document.getElementById('pl-leasing-apply-success');
		if (errorEl) {
			errorEl.hidden = true;
			errorEl.textContent = '';
		}
		if (!successEl) return;
		successEl.hidden = false;
		successEl.textContent = message;
	}

	function handleApplySubmit(e) {
		e.preventDefault();
		clearApplyFeedback();

		var nameInput = document.getElementById('pl-leasing-name');
		var phoneInput = document.getElementById('pl-leasing-phone');
		var egnInput = document.getElementById('pl-leasing-egn');
		var emailInput = document.getElementById('pl-leasing-email');
		var agreeTerms = document.getElementById('pl-leasing-agree-terms');
		var agreeApply = document.getElementById('pl-leasing-agree-apply');
		var agreePrivacy = document.getElementById('pl-leasing-agree-privacy');

		var invalid = false;
		var firstInvalid = null;

		function markInvalid(el) {
			if (!el) return;
			el.classList.add('is-invalid');
			if (el.type === 'checkbox' && el.parentElement) {
				el.parentElement.classList.add('is-invalid');
			}
			if (!firstInvalid) firstInvalid = el;
			invalid = true;
		}

		if (!isCyrillicName(nameInput && nameInput.value)) {
			markInvalid(nameInput);
		}
		if (!isPhoneStartingWithZero(phoneInput && phoneInput.value)) {
			markInvalid(phoneInput);
		}
		if (!isLikelyEgn(egnInput && egnInput.value)) {
			markInvalid(egnInput);
		}
		if (!isEmailFormat(emailInput && emailInput.value)) {
			markInvalid(emailInput);
		}
		if (!(agreeTerms && agreeTerms.checked)) {
			markInvalid(agreeTerms);
		}
		if (!(agreeApply && agreeApply.checked)) {
			markInvalid(agreeApply);
		}
		if (!(agreePrivacy && agreePrivacy.checked)) {
			markInvalid(agreePrivacy);
		}

		if (invalid) {
			showApplyError(
				'Моля попълнете коректно всички полета (име на кирилица, телефон започващ с 0, ЕГН, ел. поща) и приемете условията.'
			);
			if (firstInvalid && typeof firstInvalid.focus === 'function') {
				firstInvalid.focus();
			}
			return;
		}

		ensureSelectionValid();
		var selected = getSelectedTerm();
		var columnTitle = (COLUMNS[state.column] && COLUMNS[state.column].title) || state.column;
		var payload = {
			fullName: String(nameInput.value || '').trim(),
			phone: String(phoneInput.value || '').trim(),
			egn: String(egnInput.value || '').replace(/\s+/g, ''),
			email: String(emailInput.value || '').trim(),
			column: state.column,
			provider: COLUMNS[state.column] && COLUMNS[state.column].provider,
			columnTitle: columnTitle,
			months: selected.months,
			monthly: selected.monthly,
			total: selected.total,
			promoCode: state.promoCode,
			downPayment: state.downPayment,
			price: state.price,
			financed: getFinancedAmount(),
			prodId: state.prodId,
		};

		if (typeof console !== 'undefined' && console.log) {
			console.log('[PlasicoLeasing] local apply (no backend)', payload);
		}

		showApplySuccess(
			'Заявката е приета локално (без изпращане). Избрана схема: ' +
				columnTitle +
				' — ' +
				selected.months +
				' вноски × ' +
				formatEuro(selected.monthly) +
				'.'
		);
	}

	function applyToolbarInputs() {
		var promoInput = document.getElementById('pl-leasing-promo');
		var downInput = document.getElementById('pl-leasing-down');
		if (promoInput) {
			state.promoCode = String(promoInput.value || '').trim();
		}
		if (downInput) {
			var parsed = parseLooseAmount(downInput.value);
			if (parsed > state.price) parsed = state.price;
			state.downPayment = parsed;
		}
	}

	function syncToolbarInputs() {
		var promoInput = document.getElementById('pl-leasing-promo');
		var downInput = document.getElementById('pl-leasing-down');
		if (promoInput && document.activeElement !== promoInput) {
			promoInput.value = state.promoCode || '';
		}
		if (downInput && document.activeElement !== downInput) {
			downInput.value = formatEuro(state.downPayment || 0);
		}
	}

	function renderGrid() {
		var grid = document.getElementById('pl-leasing-grid');
		if (!grid) return;

		var header =
			'<div class="pl-leasing-grid-row pl-leasing-grid-row--head" role="row">' +
			'<div class="pl-leasing-grid-corner" role="columnheader"></div>' +
			'<div class="pl-leasing-grid-colhead" role="columnheader">' +
			COLUMNS.personal.title +
			'</div>' +
			'<div class="pl-leasing-grid-colhead pl-leasing-grid-colhead--postbank" role="columnheader">' +
			COLUMNS.postbank.title +
			'</div>' +
			'</div>';

		var rows = MONTH_ROWS.map(function (months) {
			var personalTerm = findColumnTerm('personal', months);
			var postbankTerm = findColumnTerm('postbank', months);
			return (
				'<div class="pl-leasing-grid-row" role="row">' +
				'<div class="pl-leasing-grid-month" role="rowheader">' +
				months +
				' месеца</div>' +
				schemeCardHtml('personal', personalTerm) +
				schemeCardHtml('postbank', postbankTerm) +
				'</div>'
			);
		}).join('');

		grid.innerHTML = header + rows;

		Array.prototype.slice
			.call(grid.querySelectorAll('.pl-leasing-radio'))
			.forEach(function (radio) {
				radio.addEventListener('change', function () {
					if (!radio.checked) return;
					var columnId = radio.getAttribute('data-column');
					var months = Number(radio.getAttribute('data-months'));
					state.column = columnId;
					state.selectedMonths = months;
					if (columnId === 'personal') {
						state.personalMonths = months;
					}
					renderModal();
					renderTeaser();
				});
			});
	}

	function renderModal() {
		ensureModal();
		ensureSelectionValid();
		ensurePersonalMonthsValid();
		syncToolbarInputs();

		var selected = getSelectedTerm();
		document.getElementById('pl-leasing-summary').textContent = summaryText(selected);
		renderGrid();
	}

	function syncLeasingControls() {
		var hasPrice = state.price > 0;
		document.querySelectorAll('.js-open-leasing').forEach(function (btn) {
			btn.hidden = !hasPrice;
		});
	}

	function renderTeaser() {
		var holders = document.querySelectorAll('#load-leasing, .load-leasing');
		if (!holders.length) return;

		if (!state.price) {
			holders.forEach(function (holder) {
				holder.innerHTML = '';
			});
			syncLeasingControls();
			return;
		}

		var term = getTeaserTerm();
		var html =
			'<a href="#" class="pl-leasing-teaser js-open-leasing" data-leasing-column="personal">' +
			teaserText(term) +
			'</a>';

		holders.forEach(function (holder) {
			holder.innerHTML = html;
		});
		syncLeasingControls();
	}

	function refresh() {
		state.price = parsePrice();
		if (state.downPayment > state.price) {
			state.downPayment = state.price;
		}
		renderTeaser();
		var overlay = document.getElementById('pl-leasing-overlay');
		if (overlay && !overlay.hidden) {
			renderModal();
		}
	}

	function resolveColumnFromOptions(options) {
		if (!options) return 'personal';
		if (options.column && COLUMNS[options.column]) return options.column;
		if (
			options.provider === 'postbank' ||
			options.provider === 'card' ||
			options.provider === 'bnp-card'
		) {
			return 'postbank';
		}
		if (options.provider === 'bnp' || options.provider === 'unicredit') {
			return 'personal';
		}
		return 'personal';
	}

	function openModal(options) {
		state.column = resolveColumnFromOptions(options);
		state.price = parsePrice();
		state.prodId = getProdId();
		ensurePersonalMonthsValid();

		if (state.column === 'personal') {
			state.selectedMonths = state.personalMonths;
		} else {
			ensureSelectionValid();
		}

		if (!state.price) return;

		renderModal();
		clearApplyFeedback();
		var overlay = ensureModal();
		overlay.hidden = false;
		document.body.style.overflow = 'hidden';
	}

	function closeModal() {
		var overlay = document.getElementById('pl-leasing-overlay');
		if (!overlay) return;
		overlay.hidden = true;
		document.body.style.overflow = '';
	}

	function shouldHandleLocally() {
		return (
			document.body.id === 'product_preview' ||
			document.getElementById('load-leasing') ||
			document.querySelector('.load-leasing') ||
			document.querySelector('.js-open-leasing') ||
			document.querySelector('[data-url^="leasing"]') ||
			document.getElementById('cart-drawer-subtotal') ||
			document.getElementById('checkout') ||
			document.querySelector('.checkout-mock')
		);
	}

	function bindTriggers() {
		document.body.addEventListener(
			'click',
			function (e) {
				var trigger = e.target.closest(
					'[data-url^="leasing"], .js-open-leasing, #load-leasing a, .load-leasing a'
				);
				if (!trigger) return;

				e.preventDefault();
				e.stopPropagation();
				openModal({ column: 'personal' });
				return false;
			},
			true
		);

		document.body.addEventListener('click', function (e) {
			var option = e.target.closest('.installment-option[data-installment]');
			if (!option) return;

			var kind = option.getAttribute('data-installment');
			if (kind === 'bnp-card') {
				openModal({ column: 'postbank', provider: 'bnp-card' });
				return;
			}
			if (kind === 'bnp') {
				openModal({ column: 'personal', provider: 'bnp' });
			}
		});
	}

	function init() {
		if (!shouldHandleLocally()) return;

		state.price = parsePrice();
		state.prodId = getProdId();
		state.personalMonths = DEFAULT_PERSONAL_MONTHS;
		state.selectedMonths = DEFAULT_PERSONAL_MONTHS;
		state.column = 'personal';
		renderTeaser();
		bindTriggers();

		document.addEventListener('plasico:cart-updated', refresh);

		window.PlasicoLeasing = {
			open: openModal,
			close: closeModal,
			refresh: refresh,
			getState: function () {
				var selected = getSelectedTerm();
				var teaser = getTeaserTerm();
				return {
					price: state.price,
					downPayment: state.downPayment,
					promoCode: state.promoCode,
					financed: getFinancedAmount(),
					prodId: state.prodId,
					column: state.column,
					provider: COLUMNS[state.column].provider,
					selectedMonths: state.selectedMonths,
					personalMonths: state.personalMonths,
					selected: selected,
					teaser: teaser,
				};
			},
		};
	}

	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', init);
	} else {
		init();
	}

	window.addEventListener('load', function () {
		if (!shouldHandleLocally()) return;
		refresh();
	});
})();
