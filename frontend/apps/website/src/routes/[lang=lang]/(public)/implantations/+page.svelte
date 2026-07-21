<script lang="ts">
	import { MapPin, Phone, WhatsappLogo } from 'phosphor-svelte';
	import CoteDIvoireMap from '$lib/illustrations/CoteDIvoireMap.svelte';
	import KenteMotif from '$lib/illustrations/KenteMotif.svelte';
	import { reveal } from '$lib/actions/reveal';
	import { LOCATION_STATUS_LABELS } from '$lib/content';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const headquarters = $derived(data.locations.find((item) => item.status === 'headquarters'));
	const otherLocations = $derived(data.locations.filter((item) => item.status !== 'headquarters'));
</script>

<svelte:head>
	<title>Nos implantations, IUMC</title>
	<meta
		name="description"
		content="Le siège d'IUMC est à Bouaké. Découvrez les villes de Côte d'Ivoire concernées par l'expansion progressive d'IUMC."
	/>
</svelte:head>

<section class="mx-auto grid max-w-7xl items-center gap-12 overflow-hidden px-6 pt-16 pb-16 md:grid-cols-2 lg:px-10">
	<div use:reveal>
		<h1 class="text-4xl font-semibold text-ink-950 md:text-5xl">Nos implantations</h1>
		<p class="mt-4 max-w-[50ch] text-ink-800/80">
			Le siège d'IUMC est situé à Bouaké. L'entreprise prévoit d'étendre
			<span class="font-bold text-gold-600">progressivement</span> sa présence à plusieurs
			villes de Côte d'Ivoire.
		</p>
	</div>
	<div class="parallax-lent mx-auto w-full max-w-sm md:max-w-none" use:reveal={{ delay: 120 }}>
		<CoteDIvoireMap class="h-auto w-full" />
	</div>
</section>

{#if headquarters}
	<section class="mx-auto max-w-7xl px-6 pb-10 lg:px-10">
		<div
			use:reveal
			class="relative flex flex-col gap-6 overflow-hidden rounded-card bg-ink-950 p-8 text-paper-50 sm:flex-row sm:items-center sm:justify-between"
		>
			<KenteMotif
				patternId="kente-siege"
				class="pointer-events-none absolute inset-0 h-full w-full text-paper-50 opacity-5"
			/>
			<div class="relative">
				<span class="rounded-pill bg-gold-500/15 px-3 py-1 text-xs font-medium text-gold-500">
					{LOCATION_STATUS_LABELS[headquarters.status] ?? headquarters.status}
				</span>
				<h2 class="mt-3 text-2xl font-semibold">{headquarters.city}</h2>
				{#if headquarters.address}
					<p class="mt-1 flex items-center gap-2 text-sm text-paper-100/70">
						<MapPin size={16} />
						{headquarters.address}
					</p>
				{/if}
			</div>
			<div class="relative flex flex-wrap gap-3">
				{#if headquarters.phone}
					<a
						href={`tel:${headquarters.phone.replace(/\s+/g, '')}`}
						class="inline-flex items-center gap-2 rounded-pill border border-paper-100/25 px-5 py-2.5 text-sm font-medium hover:border-paper-100/50"
					>
						<Phone size={16} />
						Appeler
					</a>
				{/if}
				{#if headquarters.whatsapp}
					<a
						href={`https://wa.me/${headquarters.whatsapp.replace(/\D/g, '')}`}
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
					>
						<WhatsappLogo size={16} weight="fill" />
						WhatsApp
					</a>
				{/if}
			</div>
		</div>
	</section>
{/if}

<section class="mx-auto max-w-7xl px-6 pb-20 lg:px-10">
	<h2 class="text-xl font-semibold text-ink-950">Expansion progressive</h2>
	<p class="mt-2 max-w-[60ch] text-sm text-ink-800/70">
		Ces villes sont concernées par l'ouverture progressive de nouvelles implantations. Les
		coordonnées locales seront publiées à l'ouverture de chaque agence.
	</p>

	<div class="mt-6 flex flex-wrap gap-3">
		{#each otherLocations as location, i (location.city)}
			<span
				use:reveal={{ delay: i * 25 }}
				class="inline-flex items-center gap-2 rounded-pill border border-ink-900/15 bg-paper-50 px-4 py-2 text-sm text-ink-900"
			>
				<MapPin size={14} class="text-ink-800/50" />
				{location.city}
			</span>
		{/each}
	</div>
</section>
