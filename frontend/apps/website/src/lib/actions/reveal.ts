import type { Action } from 'svelte/action';

/**
 * Révèle un élément (fondu + léger décalage vertical) quand il entre dans le
 * viewport. Basé sur IntersectionObserver (jamais d'écouteur de scroll).
 * Respecte prefers-reduced-motion : l'élément apparaît alors immédiatement.
 */
export const reveal: Action<HTMLElement, { delay?: number } | undefined> = (node, options) => {
	const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

	if (prefersReduced) {
		return {};
	}

	node.classList.add('reveal-init');
	node.style.transitionDelay = `${options?.delay ?? 0}ms`;

	const observer = new IntersectionObserver(
		(entries) => {
			for (const entry of entries) {
				if (entry.isIntersecting) {
					node.classList.add('reveal-in');
					observer.unobserve(node);
				}
			}
		},
		{ threshold: 0.15 }
	);
	observer.observe(node);

	return {
		destroy() {
			observer.disconnect();
		}
	};
};
