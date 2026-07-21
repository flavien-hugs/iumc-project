<script lang="ts">
	/**
	 * Motif géométrique originel inspiré des poids à peser l'or baoulé
	 * (Côte d'Ivoire) : losanges concentriques. Composition abstraite propre,
	 * pensée comme filigrane décoratif (grande taille, faible opacité),
	 * pas une reproduction de pièce précise.
	 */
	let { class: className = '' }: { class?: string } = $props();
</script>

<svg
	viewBox="0 0 200 200"
	class={className}
	fill="none"
	stroke="currentColor"
	stroke-width="1.5"
	xmlns="http://www.w3.org/2000/svg"
	aria-hidden="true"
>
	<rect x="20" y="20" width="160" height="160" transform="rotate(45 100 100)" />
	<rect x="52" y="52" width="96" height="96" transform="rotate(45 100 100)" />
	<rect x="84" y="84" width="32" height="32" transform="rotate(45 100 100)" />
	<circle cx="100" cy="100" r="5" fill="currentColor" stroke="none" />
</svg>
