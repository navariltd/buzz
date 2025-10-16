// Currency formatting utilities using JavaScript Intl API

export function formatCurrency(amount, currencyCode = "INR", locale = "en-US") {
	try {
		return new Intl.NumberFormat(locale, {
			style: "currency",
			currency: currencyCode,
		}).format(amount);
	} catch (error) {
		// Fallback if currency code is invalid or not supported
		console.warn(
			`Invalid currency code: ${currencyCode}. Falling back to default formatting.`
		);
		return new Intl.NumberFormat(locale, {
			style: "currency",
			currency: "INR",
		}).format(amount);
	}
}

export function formatPrice(price, currencyCode = "INR", locale = "en-US") {
	return formatCurrency(price, currencyCode, locale);
}

export function formatPriceOrFree(price, currencyCode = "INR", locale = "en-US") {
	if (price === 0 || price === "0") {
		return "Free";
	}
	return formatPrice(price, currencyCode, locale);
}

export function getCurrencySymbol(currencyCode, locale = "en-US") {
	try {
		const formatter = new Intl.NumberFormat(locale, {
			style: "currency",
			currency: currencyCode,
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		});

		// Format a small number and extract just the symbol
		const formatted = formatter.format(0);
		return formatted.replace(/[\d\s,]/g, "").trim();
	} catch (error) {
		console.warn(`Invalid currency code: ${currencyCode}`);
		return currencyCode;
	}
}
