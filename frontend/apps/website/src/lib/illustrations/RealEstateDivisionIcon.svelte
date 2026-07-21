<script lang="ts">
	/** Icône ligne maison : bâtiment et parcelle, pour le pôle Foncier et immobilier. */
	let { class: className = '' }: { class?: string } = $props();
</script>

<svg
	viewBox="0 0 48 48"
	class={className}
	fill="none"
	stroke="currentColor"
	stroke-width="1.75"
	stroke-linecap="round"
	stroke-linejoin="round"
	xmlns="http://www.w3.org/2000/svg"
	aria-hidden="true"
>
	<path d="M14 22 L24 12 L34 22" />
	<path d="M16 20 V34 H32 V20" />
	<line x1="24" y1="34" x2="24" y2="26" />

	<rect x="6" y="38" width="36" height="4" rx="1" opacity="0.5" />
	<line x1="6" y1="38" x2="6" y2="34" stroke-dasharray="2 3" opacity="0.5" />
	<line x1="42" y1="38" x2="42" y2="34" stroke-dasharray="2 3" opacity="0.5" />
</svg>
