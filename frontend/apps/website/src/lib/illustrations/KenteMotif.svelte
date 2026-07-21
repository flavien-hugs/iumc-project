<script lang="ts">
	/**
	 * Motif tissé inspiré des étoffes kente (aire culturelle akan, Ghana et
	 * Côte d'Ivoire) : alternance en damier de bandes rayées et de losanges,
	 * évoquant les lés cousus des pagnes tissés. Composition géométrique
	 * originale, pas une reproduction d'un motif traditionnel précis.
	 * Les rayures sont dorées (accent unique du site) ; les losanges héritent
	 * de currentColor pour s'adapter aux fonds clairs comme sombres.
	 * `patternId` doit être unique par instance sur une même page.
	 */
	let { class: className = '', patternId = 'kente' }: { class?: string; patternId?: string } =
		$props();
</script>

<svg class={className} xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
	<defs>
		<pattern id={patternId} width="80" height="80" patternUnits="userSpaceOnUse">
			<g fill="var(--color-green-500)">
				<rect x="3" y="4" width="4" height="32" />
				<rect x="11" y="4" width="4" height="32" />
				<rect x="19" y="4" width="4" height="32" />
				<rect x="27" y="4" width="4" height="32" />
				<rect x="35" y="4" width="4" height="32" />
			</g>
			<path d="M60,6 L74,20 L60,34 L46,20 Z" fill="none" stroke="currentColor" stroke-width="2" />
			<circle cx="60" cy="20" r="2" fill="currentColor" />

			<path d="M20,46 L34,60 L20,74 L6,60 Z" fill="none" stroke="currentColor" stroke-width="2" />
			<circle cx="20" cy="60" r="2" fill="currentColor" />
			<g fill="var(--color-green-500)">
				<rect x="43" y="44" width="4" height="32" />
				<rect x="51" y="44" width="4" height="32" />
				<rect x="59" y="44" width="4" height="32" />
				<rect x="67" y="44" width="4" height="32" />
				<rect x="75" y="44" width="4" height="32" />
			</g>

			<!-- lisières horizontales entre les lés -->
			<rect x="0" y="39" width="80" height="1" fill="currentColor" opacity="0.4" />
			<rect x="0" y="79" width="80" height="1" fill="currentColor" opacity="0.4" />
		</pattern>
	</defs>
	<rect width="100%" height="100%" fill={`url(#${patternId})`} />
</svg>
