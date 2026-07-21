<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { apiCall } from '@iumc/api';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	const DIVISION_STATUS_LABELS: Record<string, string> = {
		active: 'Actif',
		coming_soon: 'Bientôt disponible',
		inactive: 'Inactif',
		hidden: 'Masqué'
	};

	async function setDivisionStatus(id: number, status: string) {
		await apiCall(`/admin/divisions/${id}`, { method: 'PATCH', body: { status } });
		await invalidateAll();
	}

	async function toggleService(id: number, status: string) {
		await apiCall(`/admin/services/${id}`, {
			method: 'PATCH',
			body: { status: status === 'active' ? 'inactive' : 'active' }
		});
		await invalidateAll();
	}
</script>

<svelte:head>
	<title>Pôles et services, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Pôles & services</h1>
<p class="mt-2 text-sm text-ink-800/70">
	Activez, masquez ou désactivez les pôles et services affichés sur le site public. L'édition
	des contenus détaillés arrivera avec le module complet.
</p>

<div class="mt-8 space-y-6">
	{#each data.divisions as division (division.id)}
		<section class="rounded-card border border-ink-900/10 bg-paper-50 p-5">
			<div class="flex flex-wrap items-center justify-between gap-3">
				<h2 class="text-lg font-semibold text-ink-950">{division.name}</h2>
				<select
					value={division.status}
					onchange={(event) => setDivisionStatus(division.id, event.currentTarget.value)}
					aria-label={`Statut du pôle ${division.name}`}
					class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-1.5 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
				>
					{#each Object.entries(DIVISION_STATUS_LABELS) as [value, label] (value)}
						<option {value}>{label}</option>
					{/each}
				</select>
			</div>
			{#if division.services.length === 0}
				<p class="mt-3 text-sm text-ink-800/60">Aucun service pour ce pôle.</p>
			{:else}
				<ul class="mt-4 divide-y divide-ink-900/5">
					{#each division.services as service (service.id)}
						<li class="flex items-center justify-between gap-4 py-2.5 text-sm">
							<span class={service.status === 'active' ? 'text-ink-950' : 'text-ink-800/50 line-through'}>
								{service.title}
							</span>
							<button
								type="button"
								onclick={() => toggleService(service.id, service.status)}
								class={`rounded-pill px-3 py-1 text-xs font-medium whitespace-nowrap ${
									service.status === 'active'
										? 'bg-gold-500/15 text-gold-600 hover:bg-gold-500/25'
										: 'bg-ink-900/5 text-ink-800/60 hover:bg-ink-900/10'
								}`}
							>
								{service.status === 'active' ? 'Actif' : 'Inactif'}
							</button>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
	{/each}
</div>
