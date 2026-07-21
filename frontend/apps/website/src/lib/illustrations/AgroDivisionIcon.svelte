<script lang="ts">
	/** Icône ligne maison : épi et feuille, pour le pôle Agropastoral. */
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
	<line x1="24" y1="40" x2="24" y2="10" />
	<path d="M24 12 C19 14 17 18 18 22" />
	<path d="M24 18 C29 20 31 24 30 28" />
	<path d="M24 24 C19 26 17 30 18 34" />
	<path d="M24 30 C29 32 31 35 30 38" />
</svg>
