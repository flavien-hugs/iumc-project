<script lang="ts">
	import KenteMotif from '$lib/illustrations/KenteMotif.svelte';
	import { reveal } from '$lib/actions/reveal';
	import {
		articleIcon,
		formatPublishedDate,
		stripHtml,
		type PublicArticleSummary
	} from '$lib/content';

	let {
		article,
		titleTag = 'h3',
		revealDelay = 0
	}: { article: PublicArticleSummary; titleTag?: 'h2' | 'h3'; revealDelay?: number } = $props();

	const Icon = $derived(articleIcon(article.category));
	const summaryText = $derived(stripHtml(article.summary));
</script>

<a
	href={`/fr/actualites/${article.slug}`}
	use:reveal={{ delay: revealDelay }}
	class="group flex flex-col overflow-hidden rounded-card border border-ink-900/10"
>
	<div class="relative flex h-32 items-center justify-center overflow-hidden bg-ink-950">
		<KenteMotif
			patternId={`kente-card-${article.slug}`}
			class="pointer-events-none absolute inset-0 h-full w-full text-paper-50 opacity-5"
		/>
		<Icon class="relative h-9 w-9 text-gold-500" />
	</div>
	<div class="flex flex-1 flex-col gap-2 p-6">
		{#if article.category}
			<span class="text-xs font-medium text-gold-600">{article.category}</span>
		{/if}
		<svelte:element
			this={titleTag}
			class="text-lg font-semibold text-ink-950 group-hover:underline"
		>
			{article.title}
		</svelte:element>
		{#if summaryText}
			<p class="text-sm text-ink-800/70">{summaryText}</p>
		{/if}
		<span class="mt-auto pt-3 text-xs text-ink-800/50">
			{formatPublishedDate(article.published_at)}
		</span>
	</div>
</a>
