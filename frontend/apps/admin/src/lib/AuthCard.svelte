<script lang="ts">
	import KenteMotif from '@iumc/ui/illustrations/KenteMotif.svelte';
	import GoldWeightMotif from '@iumc/ui/illustrations/GoldWeightMotif.svelte';
	import SenufoFrieze from '@iumc/ui/illustrations/SenufoFrieze.svelte';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<!-- Fond des pages d'authentification : filigrane tissé + halos de couleur +
     carte flottante, même esprit que les autres surfaces de marque du site
     (motifs déjà utilisés en filigrane sur l'accueil et « Qui sommes-nous »),
     décliné ici sur le panel. -->
<div class="relative grid min-h-dvh place-items-center overflow-hidden bg-paper-50 p-6">
	<KenteMotif
		patternId="kente-auth-bg"
		class="pointer-events-none absolute inset-0 h-full w-full text-ink-900 opacity-5"
	/>
	<GoldWeightMotif
		class="pointer-events-none absolute -right-24 -bottom-24 h-96 w-96 text-ink-900/4"
	/>
	<div
		class="pointer-events-none absolute -top-32 -right-24 h-96 w-96 rounded-full bg-green-500/15 blur-3xl"
	></div>
	<div
		class="pointer-events-none absolute -bottom-32 -left-24 h-96 w-96 rounded-full bg-gold-500/15 blur-3xl"
	></div>

	<div
		class="relative w-full max-w-sm overflow-hidden rounded-card border border-ink-900/10 bg-paper-50/95 p-8 shadow-2xl shadow-ink-950/10 backdrop-blur-sm"
	>
		<SenufoFrieze class="absolute inset-x-0 top-0 h-2 w-full text-green-500/50" />
		{@render children()}
	</div>
</div>
