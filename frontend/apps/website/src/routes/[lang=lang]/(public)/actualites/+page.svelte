<script lang="ts">
	import ArticleCard from '$lib/components/ArticleCard.svelte';
	import SenufoFrieze from '$lib/illustrations/SenufoFrieze.svelte';
	import { reveal } from '$lib/actions/reveal';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
</script>

<svelte:head>
	<title>Actualités et conseils, IUMC</title>
	<meta
		name="description"
		content="Actualités, conseils et guides pratiques sur les démarches foncières, immobilières et juridiques d'IUMC."
	/>
</svelte:head>

<section class="mx-auto max-w-7xl px-6 pt-16 pb-10 lg:px-10" use:reveal>
	<h1 class="text-4xl font-semibold text-ink-950 md:text-5xl">Actualités et conseils</h1>
	<p class="mt-4 max-w-[60ch] text-ink-800/80">
		Des repères pratiques sur les démarches foncières, immobilières et juridiques.
	</p>
</section>

<div class="mx-auto max-w-7xl px-6 lg:px-10">
	<SenufoFrieze class="h-5 w-full text-gold-500/30" />
</div>

<section class="mx-auto max-w-7xl px-6 pt-10 pb-20 lg:px-10">
	{#if data.articles.length === 0}
		<p class="text-ink-800/70">Aucune publication pour le moment. Revenez bientôt.</p>
	{:else}
		<div class="grid gap-6 md:grid-cols-3">
			{#each data.articles as article, i (article.slug)}
				<ArticleCard {article} titleTag="h2" revealDelay={(i % 3) * 60} />
			{/each}
		</div>
	{/if}
</section>
