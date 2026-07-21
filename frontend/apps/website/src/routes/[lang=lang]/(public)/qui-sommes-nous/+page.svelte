<script lang="ts">
	import { ArrowRight, Buildings, Calendar, MapPin } from 'phosphor-svelte';
	import Seo from '$lib/components/Seo.svelte';
	import SenufoFrieze from '@iumc/ui/illustrations/SenufoFrieze.svelte';
	import GoldWeightMotif from '@iumc/ui/illustrations/GoldWeightMotif.svelte';
	import KenteMotif from '@iumc/ui/illustrations/KenteMotif.svelte';
	import { reveal } from '$lib/actions/reveal';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const about = $derived(data.company.about);

	const identityItems = $derived([
		{ icon: Calendar, label: 'Date de création', value: about.founded_year },
		{ icon: Buildings, label: 'Forme juridique', value: about.legal_form },
		{ icon: MapPin, label: 'Siège', value: about.headquarters }
	]);

	const keyFigures = $derived([
		{ value: about.founded_year, label: 'Année de création' },
		{ value: String(data.divisions?.length ?? 0), label: "Pôles d'activité" },
		{
			value: String(Math.max(0, data.locationsCount - 1)),
			label: "Villes concernées par l'expansion"
		},
		{ value: '1', label: 'Siège opérationnel, à Bouaké' }
	]);
</script>

<Seo
	title="Qui sommes-nous, IUMC"
	description="IUMC, entreprise ivoirienne créée en 2026 : histoire, vision, missions et valeurs."
/>

<section class="mx-auto max-w-3xl px-6 pt-16 pb-10 lg:px-10" use:reveal>
	<h1 class="text-4xl font-semibold text-ink-950 md:text-5xl">Qui sommes-nous ?</h1>
	<p class="mt-5 max-w-[60ch] text-lg text-ink-800/80">
		Ivoire Univers Multiservices et Commerces accompagne particuliers, entreprises et
		investisseurs dans leurs démarches juridiques, foncières, immobilières et, à terme,
		agropastorales, depuis son <span class="font-bold text-green-600">siège de Bouaké</span>.
	</p>
</section>

<div class="mx-auto max-w-3xl px-6 lg:px-10">
	<SenufoFrieze class="h-5 w-full text-gold-500/30" />
</div>

<section class="mx-auto max-w-3xl px-6 pb-16 lg:px-10">
	<div class="grid gap-6 pt-8 sm:grid-cols-3">
		{#each identityItems as item, i (item.label)}
			<div use:reveal={{ delay: i * 90 }} class="flex items-start gap-3">
				<item.icon size={20} class="mt-0.5 shrink-0 text-ink-800/50" />
				<div>
					<p class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">
						{item.label}
					</p>
					<p class="mt-1 text-sm font-medium text-ink-950">{item.value}</p>
				</div>
			</div>
		{/each}
	</div>
</section>

<section class="relative overflow-hidden bg-ink-950">
	<GoldWeightMotif
		class="parallax-lent pointer-events-none absolute top-1/2 right-0 h-105 w-105 translate-x-1/3 -translate-y-1/2 text-paper-50/5"
	/>
	<div class="relative mx-auto max-w-3xl px-6 py-16 lg:px-10" use:reveal>
		<p class="text-xs font-medium tracking-wide text-green-500/80 uppercase">
			Vision à l'horizon 2030
		</p>
		<div class="iumc-rich-text vision-content mt-4 font-display text-2xl leading-snug text-paper-50 italic md:text-3xl">
			{@html about.vision}
		</div>
	</div>
</section>

<section class="mx-auto max-w-3xl px-6 py-16 lg:px-10">
	<h2 class="text-2xl font-semibold text-ink-950">Nos missions</h2>
	<p class="mt-3 max-w-[60ch] text-sm text-ink-800/70">
		Les domaines dans lesquels IUMC accompagne ses clients, avec un développement progressif
		vers l'agropastoral, le commerce et la logistique.
	</p>
	<ul class="mt-6 divide-y divide-ink-900/10 border-t border-ink-900/10">
		{#each about.missions as mission, i (mission)}
			<li use:reveal={{ delay: i * 60 }} class="flex gap-3 py-3 text-sm text-ink-800">
				<span class="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-green-500"></span>
				{mission}
			</li>
		{/each}
	</ul>
</section>

<section class="relative overflow-hidden bg-paper-100">
	<KenteMotif
		patternId="kente-valeurs"
		class="pointer-events-none absolute inset-0 h-full w-full text-ink-700 opacity-10"
	/>
	<div class="relative mx-auto max-w-3xl px-6 py-16 text-center lg:px-10" use:reveal>
		<h2 class="text-2xl font-semibold text-ink-950">Nos valeurs</h2>
		<div class="mt-6 flex flex-wrap justify-center gap-3">
			{#each about.values as value (value)}
				<span
					class="rounded-pill border border-ink-900/15 bg-paper-50 px-4 py-2 text-sm text-ink-900"
				>
					{value}
				</span>
			{/each}
		</div>
	</div>
</section>

<section class="mx-auto max-w-3xl px-6 py-16 lg:px-10">
	<h2 class="text-2xl font-semibold text-ink-950">L'originalité du modèle IUMC</h2>
	<p class="mt-3 max-w-[60ch] text-sm text-ink-800/70">
		Prestataire pluridisciplinaire de l'ingénierie immobilière, IUMC se veut un acteur clé et
		un relais fiable des services de l'État — à travers des packages de services sur mesure et
		un modèle de gestion intégrée.
	</p>
	<dl class="mt-6 grid gap-x-10 gap-y-6 sm:grid-cols-2">
		{#each about.differentiators as item, i (item.title)}
			<div use:reveal={{ delay: i * 90 }}>
				<dt class="font-medium text-ink-950">{item.title}</dt>
				<dd class="iumc-rich-text mt-1.5 text-sm text-ink-800/70">{@html item.description}</dd>
			</div>
		{/each}
	</dl>
</section>

<section class="mx-auto max-w-3xl px-6 py-16 lg:px-10" use:reveal>
	<div class="rounded-card border border-ink-900/10 bg-paper-100 p-8 text-center">
		<p class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">
			Message de la direction
		</p>
		<p class="mt-4 font-display text-xl leading-snug text-ink-950 italic">
			Notre ambition est de rendre les démarches juridiques, foncières et immobilières
			lisibles et sereines pour chacun de nos clients, avec la même exigence à chaque étape.
		</p>
		<p class="mt-4 text-sm text-ink-800/60">La direction d'IUMC</p>
	</div>
</section>

<section class="mx-auto max-w-5xl px-6 py-16 lg:px-10">
	<div class="grid gap-8 border-t border-ink-900/10 pt-10 sm:grid-cols-4">
		{#each keyFigures as figure, i (figure.label)}
			<div use:reveal={{ delay: i * 90 }} class="text-center sm:text-left">
				<p class="font-display text-4xl font-bold text-green-600">{figure.value}</p>
				<p class="mt-1 text-sm text-ink-800/60">{figure.label}</p>
			</div>
		{/each}
	</div>
	<p class="mt-8 text-xs text-ink-800/50">
		D'autres indicateurs (clients accompagnés, dossiers traités, partenaires) seront publiés
		au fil de l'activité d'IUMC.
	</p>
</section>

<section class="bg-ink-950">
	<div class="mx-auto max-w-7xl px-6 pt-10 lg:px-10">
		<SenufoFrieze class="h-6 w-full text-gold-500/30" />
	</div>
	<div
		class="mx-auto flex max-w-7xl flex-col items-start gap-6 px-6 pt-6 pb-16 lg:flex-row lg:items-center lg:justify-between lg:px-10"
		use:reveal
	>
		<div>
			<h2 class="max-w-[24ch] text-3xl font-semibold text-paper-50">
				Envie d'échanger avec <span class="font-bold text-green-500">IUMC</span> ?
			</h2>
			<p class="mt-3 max-w-[48ch] text-paper-100/70">
				Découvrez nos pôles d'activité ou décrivez directement votre besoin.
			</p>
		</div>
		<div class="flex flex-nowrap items-center gap-3 overflow-x-auto pb-1 sm:gap-4">
			<a
				href="/fr/demande"
				class="inline-flex shrink-0 items-center gap-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium whitespace-nowrap text-ink-950 transition-transform hover:bg-green-600 active:scale-[0.98] sm:px-6 sm:py-3"
			>
				Demander un accompagnement
				<ArrowRight size={16} />
			</a>
			<a
				href="/fr/services"
				class="inline-flex shrink-0 items-center gap-2 rounded-pill border border-paper-100/25 px-5 py-2.5 text-sm font-medium whitespace-nowrap text-paper-50 hover:border-paper-100/50 sm:px-6 sm:py-3"
			>
				Découvrir nos pôles
			</a>
		</div>
	</div>
</section>

<style>
	/* Sur fond sombre, un passage mis en gras dans la vision reprend l'accent
	   or de la plateforme plutôt qu'un simple gras blanc, et sort de l'italique
	   ambiant pour rester lisible. */
	.vision-content :global(strong) {
		color: var(--color-green-500);
		font-style: normal;
	}
</style>
