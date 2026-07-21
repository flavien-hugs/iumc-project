<script lang="ts">
	/** Icône ligne maison : balance de justice, pour le pôle Services juridiques. */
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
	<line x1="24" y1="8" x2="24" y2="38" />
	<line x1="14" y1="40" x2="34" y2="40" />
	<line x1="10" y1="14" x2="38" y2="14" />
	<circle cx="24" cy="8" r="2" />

	<path d="M10 14 L5 24 A6 6 0 0 0 15 24 Z" />
	<path d="M38 14 L33 24 A6 6 0 0 0 43 24 Z" />
</svg>
