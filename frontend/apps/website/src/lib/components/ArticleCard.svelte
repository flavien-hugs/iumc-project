<script lang="ts">
	import KenteMotif from '@iumc/ui/illustrations/KenteMotif.svelte';
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
		revealDelay = 0,
		featured = false
	}: {
		article: PublicArticleSummary;
		titleTag?: 'h2' | 'h3';
		revealDelay?: number;
		featured?: boolean;
	} = $props();

	const Icon = $derived(articleIcon(article.category));
	const summaryText = $derived(stripHtml(article.summary));
</script>

{#if featured}
	<a
		href={`/fr/actualites/${article.slug}`}
		use:reveal={{ delay: revealDelay }}
		class="group flex flex-col overflow-hidden rounded-card border border-ink-900/10 bg-paper-50 transition duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-ink-950/10 motion-reduce:transition-none motion-reduce:hover:translate-y-0 md:flex-row md:items-stretch"
	>
		<div
			class="relative flex h-40 shrink-0 items-center justify-center overflow-hidden bg-ink-950 md:h-auto md:w-2/5"
		>
			<KenteMotif
				patternId={`kente-card-${article.slug}`}
				class="pointer-events-none absolute inset-0 h-full w-full text-paper-50 opacity-8"
			/>
			<Icon
				class="relative h-14 w-14 text-green-500 transition-transform duration-300 group-hover:scale-110 motion-reduce:transition-none"
			/>
		</div>
		<div class="flex flex-1 flex-col justify-center gap-3 p-8">
			{#if article.category}
				<span class="text-xs font-medium tracking-wide text-green-600 uppercase"
					>{article.category}</span
				>
			{/if}
			<svelte:element
				this={titleTag}
				class="text-2xl font-semibold text-ink-950 group-hover:underline md:text-3xl"
			>
				{article.title}
			</svelte:element>
			{#if summaryText}
				<p class="max-w-[52ch] text-sm text-ink-800/70">{summaryText}</p>
			{/if}
			<span class="text-xs text-ink-800/50">{formatPublishedDate(article.published_at)}</span>
		</div>
	</a>
{:else}
	<a
		href={`/fr/actualites/${article.slug}`}
		use:reveal={{ delay: revealDelay }}
		class="group flex flex-col overflow-hidden rounded-card border border-ink-900/10 bg-paper-50 transition duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-ink-950/8 motion-reduce:transition-none motion-reduce:hover:translate-y-0"
	>
		<div class="relative flex h-32 items-center justify-center overflow-hidden bg-ink-950">
			<KenteMotif
				patternId={`kente-card-${article.slug}`}
				class="pointer-events-none absolute inset-0 h-full w-full text-paper-50 opacity-5"
			/>
			<Icon
				class="relative h-9 w-9 text-green-500 transition-transform duration-300 group-hover:scale-110 motion-reduce:transition-none"
			/>
		</div>
		<div class="flex flex-1 flex-col gap-2 p-6">
			{#if article.category}
				<span class="text-xs font-medium text-green-600">{article.category}</span>
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
{/if}
