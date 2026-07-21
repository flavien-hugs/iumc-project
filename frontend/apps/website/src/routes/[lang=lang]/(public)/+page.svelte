<script lang="ts">
	import { ArrowRight, WhatsappLogo } from 'phosphor-svelte';
	import CoteDIvoireMap from '$lib/illustrations/CoteDIvoireMap.svelte';
	import SenufoFrieze from '$lib/illustrations/SenufoFrieze.svelte';
	import GoldWeightMotif from '$lib/illustrations/GoldWeightMotif.svelte';
	import KenteMotif from '$lib/illustrations/KenteMotif.svelte';
	import ArticleCard from '$lib/components/ArticleCard.svelte';
	import { reveal } from '$lib/actions/reveal';
	import { divisionIcon, type PublicDivision } from '$lib/content';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const divisions = $derived(data.divisions as PublicDivision[]);
	const legalDivision = $derived(divisions.find((item) => item.slug === 'juridique'));
	const realEstateDivision = $derived(divisions.find((item) => item.slug === 'foncier-immobilier'));
	const agroDivision = $derived(divisions.find((item) => item.slug === 'agropastoral'));
	const LegalIcon = divisionIcon('juridique');
	const RealEstateIcon = divisionIcon('foncier-immobilier');
	const AgroIcon = divisionIcon('agropastoral');

	const latestArticles = $derived(data.articles);

	const values = $derived(data.company.about.values);
	const advantages = $derived(data.company.about.differentiators);

	const clientGroups = [
		'Particuliers',
		'Entreprises',
		'Industriels',
		'Promoteurs immobiliers',
		'Communautés villageoises',
		'Investisseurs'
	];
</script>

<svelte:head>
	<title>IUMC, accompagnement juridique, foncier, immobilier et industriel</title>
	<meta
		name="description"
		content="IUMC accompagne particuliers, entreprises et investisseurs pour leurs démarches juridiques, foncières, immobilières et industrielles en Côte d'Ivoire, depuis Bouaké."
	/>
</svelte:head>

<!-- Hero : split asymétrique, texte + carte des implantations (parallaxe),
     bordé d'un lé kente vertical comme une lisière de pagne tissé -->
<section class="relative mx-auto grid max-w-7xl items-center gap-12 overflow-hidden px-6 pt-16 pb-20 md:grid-cols-2 lg:px-10 lg:pt-20">
	<KenteMotif
		patternId="kente-hero"
		class="pointer-events-none absolute inset-y-0 right-0 hidden w-10 text-ink-700 opacity-20 lg:block"
	/>
	<div use:reveal>
		<h1 class="max-w-[16ch] text-4xl leading-[1.1] font-semibold text-ink-950 md:text-6xl">
			La <span class="font-bold text-gold-600">sécurité</span> juridique de vos projets en
			Côte d'Ivoire.
		</h1>
		<p class="mt-6 max-w-[46ch] text-base leading-relaxed text-ink-800/80">
			IUMC accompagne particuliers, entreprises et investisseurs dans leurs démarches
			juridiques, foncières, immobilières et industrielles à Bouaké.
		</p>
		<div class="mt-8 flex flex-wrap items-center gap-4">
			<a
				href="/fr/demande"
				class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98]"
			>
				Demander un accompagnement
				<ArrowRight size={16} />
			</a>
			<a
				href="/fr/services"
				class="text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
			>
				Découvrir nos pôles
			</a>
		</div>
	</div>

	<div class="parallax-lent mx-auto w-full max-w-sm md:max-w-none" use:reveal={{ delay: 120 }}>
		<CoteDIvoireMap class="h-auto w-full" />
	</div>
</section>

<div class="mx-auto max-w-7xl px-6 lg:px-10">
	<SenufoFrieze class="h-6 w-full text-gold-500/40" />
</div>

<!-- Nos pôles d'activité : bento 1 tuile en avant + 2 secondaires (3 items, 3 cellules) -->
<section class="mx-auto max-w-7xl px-6 pb-20 lg:px-10">
	<h2 class="text-3xl font-semibold text-ink-950">Nos pôles d'activité</h2>
	<p class="mt-3 max-w-[60ch] text-ink-800/80">
		Trois domaines d'intervention, pensés pour se compléter selon la nature de votre projet.
	</p>

	<div class="mt-10 grid gap-4 md:grid-cols-2">
		{#if legalDivision}
		<a
			href={`/fr/services/${legalDivision.slug}`}
			use:reveal
			class="group relative flex flex-col justify-between gap-8 overflow-hidden rounded-card bg-ink-950 p-8 text-paper-50 md:col-span-2 md:flex-row md:items-end"
		>
			<LegalIcon class="pointer-events-none absolute -top-8 -right-6 h-48 w-48 text-paper-50/6" />
			<div>
				<LegalIcon class="h-10 w-10 text-gold-500" />
				<h3 class="mt-4 text-2xl font-semibold">{legalDivision.name}</h3>
				<p class="mt-2 max-w-[48ch] text-sm text-paper-100/70">
					{legalDivision.short_description}
				</p>
			</div>
			<span
				class="inline-flex items-center gap-2 text-sm font-medium text-gold-500 group-hover:text-gold-200"
			>
				Voir le pôle
				<ArrowRight size={16} />
			</span>
		</a>
		{/if}

		{#if realEstateDivision}
		<a
			href={`/fr/services/${realEstateDivision.slug}`}
			use:reveal={{ delay: 100 }}
			class="relative flex flex-col justify-between gap-6 overflow-hidden rounded-card bg-paper-100 p-8"
		>
			<RealEstateIcon class="pointer-events-none absolute -right-6 -bottom-8 h-44 w-44 text-ink-900/6" />
			<div>
				<RealEstateIcon class="h-10 w-10 text-ink-900" />
				<h3 class="mt-4 text-xl font-semibold text-ink-950">{realEstateDivision.name}</h3>
				<p class="mt-2 text-sm text-ink-800/80">
					{realEstateDivision.short_description}
				</p>
			</div>
			<span class="inline-flex items-center gap-2 text-sm font-medium text-gold-600">
				Voir le pôle
				<ArrowRight size={16} />
			</span>
		</a>

		{/if}

		{#if agroDivision}
		<div
			use:reveal={{ delay: 180 }}
			class="relative flex flex-col justify-between gap-6 overflow-hidden rounded-card bg-forest-100 p-8"
		>
			<AgroIcon class="pointer-events-none absolute -right-8 -bottom-8 h-44 w-44 text-forest-600/8" />
			<div>
				<div class="flex items-center justify-between">
					<AgroIcon class="h-10 w-10 text-forest-600" />
					<span
						class="rounded-pill bg-forest-600/10 px-3 py-1 text-xs font-medium text-forest-600"
					>
						Bientôt disponible
					</span>
				</div>
				<h3 class="mt-4 text-xl font-semibold text-ink-950">{agroDivision.name}</h3>
				<p class="mt-2 text-sm text-ink-800/80">
					{agroDivision.short_description}
				</p>
			</div>
		</div>
		{/if}
	</div>
</section>

<!-- Ce qui nous distingue : liste 2 colonnes + clientèles en filet -->
<section class="mx-auto max-w-7xl px-6 pb-20 lg:px-10">
	<h2 class="text-3xl font-semibold text-ink-950">Ce qui distingue IUMC</h2>
	<p class="mt-3 max-w-[60ch] text-ink-800/80">
		Un modèle pensé pour <span class="font-bold text-gold-600">simplifier des démarches</span>
		habituellement fragmentées entre plusieurs interlocuteurs.
	</p>

	<dl class="mt-10 grid gap-x-12 divide-y divide-ink-900/10 md:grid-cols-2 md:divide-y-0">
		{#each advantages as advantage, i (advantage.title)}
			<div use:reveal={{ delay: i * 90 }} class="border-ink-900/10 py-6 md:border-t md:py-8">
				<dt class="text-lg font-semibold text-ink-950">{advantage.title}</dt>
				<dd class="iumc-rich-text mt-2 text-sm text-ink-800/80">{@html advantage.description}</dd>
			</div>
		{/each}
	</dl>

	<div class="mt-10 flex flex-wrap items-center gap-x-3 gap-y-2 border-t border-ink-900/10 pt-6">
		<span class="text-sm font-medium text-ink-950">Nous accompagnons :</span>
		{#each clientGroups as group (group)}
			<span class="rounded-pill bg-ink-900/5 px-3 py-1 text-xs text-ink-800">
				{group}
			</span>
		{/each}
	</div>
</section>

<!-- Nos implantations : split image (carte) + texte, parallaxe inversée -->
<section class="mx-auto grid max-w-7xl items-center gap-12 overflow-hidden px-6 pb-20 md:grid-cols-2 lg:px-10">
	<div class="order-2 md:order-1" use:reveal>
		<h2 class="text-3xl font-semibold text-ink-950">Une présence qui s'étend</h2>
		<p class="mt-4 max-w-[52ch] text-ink-800/80">
			Le siège d'IUMC est situé à Bouaké, quartier Koko. L'entreprise prévoit d'ouvrir
			<span class="font-bold text-gold-600">progressivement</span> des agences dans plusieurs
			villes de Côte d'Ivoire, dont Yamoussoukro, Abidjan, San Pedro et Korhogo.
		</p>
		<a
			href="/fr/implantations"
			class="mt-6 inline-flex items-center gap-2 text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
		>
			Voir toutes nos implantations
			<ArrowRight size={16} />
		</a>
	</div>
	<div
		class="parallax-inverse order-1 mx-auto w-full max-w-sm md:order-2 md:max-w-none"
		use:reveal={{ delay: 120 }}
	>
		<CoteDIvoireMap class="h-auto w-full" />
	</div>
</section>

<!-- Nos valeurs : filet de puces sur filigrane décoratif, fond teinté -->
<section class="relative overflow-hidden bg-paper-100">
	<GoldWeightMotif
		class="parallax-lent pointer-events-none absolute top-1/2 left-1/2 h-105 w-105 -translate-x-1/2 -translate-y-1/2 text-ink-900/4"
	/>
	<div class="relative mx-auto max-w-7xl px-6 py-16 text-center lg:px-10" use:reveal>
		<h2 class="text-3xl font-semibold text-ink-950">Nos valeurs</h2>
		<div class="mt-8 flex flex-wrap justify-center gap-3">
			{#each values as value (value)}
				<span
					class="rounded-pill border border-ink-900/15 bg-paper-50 px-4 py-2 text-sm text-ink-900"
				>
					{value}
				</span>
			{/each}
		</div>
	</div>
</section>

<!-- Actualités et conseils : grille de cartes -->
<section class="mx-auto max-w-7xl px-6 py-20 lg:px-10">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<h2 class="text-3xl font-semibold text-ink-950">Actualités et conseils</h2>
			<p class="mt-3 max-w-[60ch] text-ink-800/80">
				Des repères pratiques sur les démarches foncières, immobilières et juridiques.
			</p>
		</div>
		<a
			href="/fr/actualites"
			class="inline-flex items-center gap-2 text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
		>
			Toutes les actualités
			<ArrowRight size={16} />
		</a>
	</div>

	<div class="mt-10 grid gap-6 md:grid-cols-3">
		{#each latestArticles as article, i (article.slug)}
			<ArticleCard {article} revealDelay={i * 90} />
		{/each}
	</div>
</section>

<!-- Appel à l'action final, sur fond tissé kente -->
<section class="relative overflow-hidden bg-ink-950">
	<KenteMotif
		patternId="kente-cta"
		class="pointer-events-none absolute inset-0 h-full w-full text-paper-50 opacity-5"
	/>
	<div class="relative mx-auto max-w-7xl px-6 pt-10 lg:px-10">
		<SenufoFrieze class="h-6 w-full text-gold-500/30" />
	</div>
	<div
		class="relative mx-auto flex max-w-7xl flex-col items-start gap-6 px-6 pt-6 pb-16 lg:flex-row lg:items-center lg:justify-between lg:px-10"
		use:reveal
	>
		<div>
			<h2 class="max-w-[24ch] text-3xl font-semibold text-paper-50">
				Prêt à <span class="font-bold text-gold-500">sécuriser</span> votre projet ?
			</h2>
			<p class="mt-3 max-w-[48ch] text-paper-100/70">
				Décrivez votre besoin, un membre de l'équipe IUMC vous recontacte.
			</p>
		</div>
		<div class="flex flex-wrap items-center gap-4">
			<a
				href="/fr/demande"
				class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-6 py-3 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98]"
			>
				Demander un accompagnement
				<ArrowRight size={16} />
			</a>
			<a
				href="https://wa.me/225XXXXXXXXXX"
				target="_blank"
				rel="noopener noreferrer"
				class="inline-flex items-center gap-2 rounded-pill border border-paper-100/25 px-6 py-3 text-sm font-medium text-paper-50 hover:border-paper-100/50"
			>
				<WhatsappLogo size={18} weight="fill" />
				Échanger sur WhatsApp
			</a>
		</div>
	</div>
</section>
