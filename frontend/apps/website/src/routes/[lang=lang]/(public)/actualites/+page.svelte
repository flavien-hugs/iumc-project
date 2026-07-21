<script lang="ts">
	import { CaretLeft, CaretRight, MagnifyingGlass } from 'phosphor-svelte';
	import Seo from '$lib/components/Seo.svelte';
	import ArticleCard from '$lib/components/ArticleCard.svelte';
	import SenufoFrieze from '$lib/illustrations/SenufoFrieze.svelte';
	import { reveal } from '$lib/actions/reveal';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const articlesPage = $derived(data.articlesPage);
	const lastPage = $derived(Math.max(1, Math.ceil(articlesPage.total / articlesPage.page_size)));
	const hasFilters = $derived(Boolean(data.q || data.category));

	// Navigation entièrement par liens (SSR) : chaque combinaison de filtres est
	// une URL — pas de JS requis pour filtrer ou paginer.
	function buildUrl(overrides: { q?: string; category?: string; page?: number }): string {
		const q = overrides.q ?? data.q;
		const category = overrides.category ?? data.category;
		const page = overrides.page ?? 1;
		const params = new URLSearchParams();
		if (q) params.set('q', q);
		if (category) params.set('category', category);
		if (page > 1) params.set('page', String(page));
		const query = params.toString();
		return `/fr/actualites${query ? `?${query}` : ''}`;
	}
</script>

<Seo
	title="Actualités et conseils, IUMC"
	description="Actualités, conseils et guides pratiques sur les démarches foncières, immobilières et juridiques d'IUMC."
/>

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
	<div class="flex flex-wrap items-center justify-between gap-4">
		{#if data.categories.length > 0}
			<nav class="flex flex-wrap items-center gap-2" aria-label="Filtrer par catégorie">
				<a
					href={buildUrl({ category: '' })}
					class={`rounded-pill px-4 py-1.5 text-sm transition-colors ${
						data.category === ''
							? 'bg-ink-950 text-paper-50'
							: 'border border-ink-900/15 text-ink-900 hover:border-green-500 hover:text-green-600'
					}`}
				>
					Toutes
				</a>
				{#each data.categories as category (category)}
					<a
						href={buildUrl({ category })}
						class={`rounded-pill px-4 py-1.5 text-sm transition-colors ${
							data.category === category
								? 'bg-ink-950 text-paper-50'
								: 'border border-ink-900/15 text-ink-900 hover:border-green-500 hover:text-green-600'
						}`}
					>
						{category}
					</a>
				{/each}
			</nav>
		{:else}
			<span></span>
		{/if}

		<form method="get" class="relative" role="search">
			{#if data.category}
				<input type="hidden" name="category" value={data.category} />
			{/if}
			<label for="actualites-q" class="sr-only">Rechercher un article</label>
			<MagnifyingGlass
				size={16}
				class="pointer-events-none absolute top-1/2 left-4 -translate-y-1/2 text-ink-800/40"
			/>
			<input
				id="actualites-q"
				type="search"
				name="q"
				value={data.q}
				placeholder="Rechercher un article…"
				class="w-64 rounded-pill border border-ink-900/15 bg-paper-50 py-2 pr-4 pl-10 text-sm text-ink-950 placeholder:text-ink-800/40 focus:border-green-500 focus:outline-none"
			/>
		</form>
	</div>

	{#if hasFilters}
		<p class="mt-4 text-sm text-ink-800/60">
			{articlesPage.total}
			{articlesPage.total > 1 ? 'articles trouvés' : 'article trouvé'}
			<a
				href="/fr/actualites"
				class="ml-2 font-medium text-green-600 underline decoration-green-600/40 underline-offset-4 hover:decoration-green-600"
			>
				Réinitialiser
			</a>
		</p>
	{/if}

	{#if articlesPage.items.length === 0}
		<p class="mt-10 text-ink-800/70">
			{#if hasFilters}
				Aucun article ne correspond à cette recherche.
			{:else}
				Aucune publication pour le moment. Revenez bientôt.
			{/if}
		</p>
	{:else if !hasFilters && articlesPage.page === 1}
		<!-- Vue par défaut : premier article en avant, format éditorial -->
		<div class="mt-10 flex flex-col gap-6">
			<ArticleCard article={articlesPage.items[0]} titleTag="h2" featured />
			{#if articlesPage.items.length > 1}
				<div class="grid gap-6 md:grid-cols-3">
					{#each articlesPage.items.slice(1) as article, i (article.slug)}
						<ArticleCard {article} titleTag="h2" revealDelay={(i % 3) * 60} />
					{/each}
				</div>
			{/if}
		</div>
	{:else}
		<div class="mt-10 grid gap-6 md:grid-cols-3">
			{#each articlesPage.items as article, i (article.slug)}
				<ArticleCard {article} titleTag="h2" revealDelay={(i % 3) * 60} />
			{/each}
		</div>
	{/if}

	{#if articlesPage.total > articlesPage.page_size}
		<nav
			class="mt-12 flex items-center justify-center gap-4 text-sm"
			aria-label="Pagination des articles"
		>
			{#if articlesPage.page > 1}
				<a
					href={buildUrl({ page: articlesPage.page - 1 })}
					class="inline-flex items-center gap-1.5 rounded-pill border border-ink-900/15 px-4 py-2 text-ink-900 transition-colors hover:border-green-500 hover:text-green-600"
				>
					<CaretLeft size={14} />
					Précédent
				</a>
			{/if}
			<span class="text-ink-800/60 tabular-nums">
				Page {articlesPage.page} sur {lastPage}
			</span>
			{#if articlesPage.page < lastPage}
				<a
					href={buildUrl({ page: articlesPage.page + 1 })}
					class="inline-flex items-center gap-1.5 rounded-pill border border-ink-900/15 px-4 py-2 text-ink-900 transition-colors hover:border-green-500 hover:text-green-600"
				>
					Suivant
					<CaretRight size={14} />
				</a>
			{/if}
		</nav>
	{/if}
</section>
