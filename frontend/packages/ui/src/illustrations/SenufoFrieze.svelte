<script lang="ts">
	/**
	 * Frise géométrique originale, inspirée de l'esthétique du tissage Korhogo
	 * (pays sénoufo, nord de la Côte d'Ivoire) : motifs en chevrons/losanges.
	 * Composition originale, pas une reproduction de motif traditionnel précis.
	 */
	let { class: className = '' }: { class?: string } = $props();
</script>

<svg
	viewBox="0 0 400 40"
	preserveAspectRatio="none"
	class={className}
	xmlns="http://www.w3.org/2000/svg"
	aria-hidden="true"
>
	<defs>
		<pattern id="senufo-frise" width="40" height="40" patternUnits="userSpaceOnUse">
			<path d="M0,32 L10,8 L20,32" fill="none" stroke="currentColor" stroke-width="1.5" />
			<path d="M20,32 L30,8 L40,32" fill="none" stroke="currentColor" stroke-width="1.5" />
			<circle cx="10" cy="20" r="1.4" fill="currentColor" />
			<circle cx="30" cy="20" r="1.4" fill="currentColor" />
		</pattern>
	</defs>
	<rect width="400" height="40" fill="url(#senufo-frise)" />
</svg>
