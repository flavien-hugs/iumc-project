<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const stats = $derived(data.stats);

	const cards = $derived([
		{ label: 'Demandes au total', value: stats.total_requests, accent: true },
		{ label: 'Nouvelles demandes', value: stats.new_requests, accent: true },
		{ label: 'Demandes en cours', value: stats.in_progress_requests, accent: false },
		{ label: 'Demandes clôturées', value: stats.closed_requests, accent: false },
		{ label: 'Rendez-vous à venir', value: stats.upcoming_appointments, accent: false },
		{ label: 'Services actifs', value: stats.active_services, accent: false },
		{ label: 'Implantations', value: stats.locations, accent: false },
		{ label: 'Articles publiés', value: stats.published_articles, accent: false }
	]);
</script>

<svelte:head>
	<title>Tableau de bord, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Tableau de bord</h1>
<p class="mt-2 text-sm text-ink-800/70">Vue d'ensemble de l'activité de la plateforme.</p>

<div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
	{#each cards as card (card.label)}
		<div class="rounded-card border border-ink-900/10 bg-paper-50 p-5">
			<p
				class={`font-display text-3xl font-bold ${card.accent ? 'text-green-600' : 'text-ink-950'}`}
			>
				{card.value}
			</p>
			<p class="mt-1 text-sm text-ink-800/70">{card.label}</p>
		</div>
	{/each}
</div>

<div class="mt-8 rounded-card border border-ink-900/10 bg-paper-50 p-5">
	<p class="text-sm text-ink-800/70">
		Les répartitions par pôle, par ville et l'évolution mensuelle (PRD section 11.2) seront
		ajoutées avec le module de statistiques avancées.
	</p>
</div>
