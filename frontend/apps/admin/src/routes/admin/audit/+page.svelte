<script lang="ts">
	import { CalendarBlank, FunnelSimple } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Toolbar from '@iumc/ui/composants/Toolbar.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import { ACTION_LABELS, formatDateTime } from '$lib/labels';
	import type { AuditLogRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const logsPage = $derived(data.logsPage);

	const RESOURCE_LABELS: Record<string, string> = {
		user: 'utilisateur',
		service_request: 'demande',
		appointment: 'rendez-vous',
		division: 'pôle',
		service: 'service',
		article: 'article',
		faq: 'FAQ',
		location: 'implantation',
		media_file: 'média',
		settings: 'paramètres'
	};

	let dateFrom = $state(data.dateFrom);
	let dateTo = $state(data.dateTo);
	let refreshing = $state(false);

	function resourceLabel(entry: AuditLogRow): string {
		if (!entry.resource) return '-';
		const label = RESOURCE_LABELS[entry.resource] ?? entry.resource;
		return entry.resource_id ? `${label} #${entry.resource_id}` : label;
	}

	function applyFilters(overrides: Record<string, string> = {}) {
		const params = new URLSearchParams();
		const from = overrides.dateFrom ?? dateFrom;
		const to = overrides.dateTo ?? dateTo;
		if (from) params.set('date_from', from);
		if (to) params.set('date_to', to);
		goto(`/admin/audit${params.size > 0 ? `?${params}` : ''}`, { keepFocus: true });
	}

	async function refresh() {
		refreshing = true;
		try {
			await invalidateAll();
		} finally {
			refreshing = false;
		}
	}

	function changePage(nextPage: number) {
		const params = new URLSearchParams(page.url.searchParams);
		params.set('page', String(nextPage));
		goto(`/admin/audit?${params}`, { keepFocus: true });
	}

	let selected = $state<AuditLogRow | null>(null);
</script>

<svelte:head>
	<title>Journal d'activité, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Journal d'activité</h1>
<p class="mt-2 text-sm text-ink-800/70">Les actions sensibles du panel (PRD section 11.8).</p>

<Toolbar onRefresh={refresh} {refreshing}>
	{#snippet filters()}
		<form
			class="flex flex-wrap items-end gap-3"
			onsubmit={(event) => {
				event.preventDefault();
				applyFilters();
			}}
		>
			<div class="w-48">
				<TextField id="date-from" label="Depuis le" type="date" icon={CalendarBlank} bind:value={dateFrom} compact />
			</div>
			<div class="w-48">
				<TextField id="date-to" label="Jusqu'au" type="date" icon={CalendarBlank} bind:value={dateTo} compact />
			</div>
			<button
				type="submit"
				class="inline-flex items-center gap-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600"
			>
				<FunnelSimple size={16} />
				Filtrer
			</button>
			{#if dateFrom || dateTo}
				<button
					type="button"
					onclick={() => {
						dateFrom = '';
						dateTo = '';
						applyFilters({ dateFrom: '', dateTo: '' });
					}}
					class="rounded-pill border border-ink-900/20 px-4 py-2.5 text-sm font-medium text-ink-900 hover:border-ink-900/40"
				>
					Réinitialiser
				</button>
			{/if}
		</form>
	{/snippet}
</Toolbar>

<div class="mt-6 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
	<table class="w-full min-w-160 text-left text-sm">
		<thead>
			<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
				<th class="px-4 py-3 font-medium">#</th>
				<th class="px-4 py-3 font-medium">Date</th>
				<th class="px-4 py-3 font-medium">Utilisateur</th>
				<th class="px-4 py-3 font-medium">Action</th>
				<th class="px-4 py-3 font-medium">Ressource</th>
				<th class="px-4 py-3 font-medium">Adresse IP</th>
			</tr>
		</thead>
		<tbody class="divide-y divide-ink-900/5">
			{#each logsPage.items as entry, i (entry.id)}
				<tr class="cursor-pointer hover:bg-ink-900/4" onclick={() => (selected = entry)}>
					<td class="px-4 py-3 text-ink-800/50 tabular-nums">
						{(logsPage.page - 1) * logsPage.page_size + i + 1}
					</td>
					<td class="px-4 py-3 whitespace-nowrap text-ink-800/70">
						{formatDateTime(entry.created_at)}
					</td>
					<td class="px-4 py-3 text-ink-950">{entry.user_name ?? '-'}</td>
					<td class="px-4 py-3 text-ink-800">{ACTION_LABELS[entry.action] ?? entry.action}</td>
					<td class="px-4 py-3 text-ink-800/70">{resourceLabel(entry)}</td>
					<td class="px-4 py-3 text-ink-800/60">{entry.ip_address ?? '-'}</td>
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<Pagination
	page={logsPage.page}
	pageSize={logsPage.page_size}
	total={logsPage.total}
	onchange={changePage}
/>

<Drawer open={selected !== null} title="Détail de l'évènement" onclose={() => (selected = null)}>
	{#if selected}
		<dl class="flex flex-col gap-4 text-sm">
			<div>
				<dt class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">Date</dt>
				<dd class="mt-1 text-ink-950">{formatDateTime(selected.created_at)}</dd>
			</div>
			<div>
				<dt class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">Utilisateur</dt>
				<dd class="mt-1 text-ink-950">{selected.user_name ?? 'Système'}</dd>
			</div>
			<div>
				<dt class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">Action</dt>
				<dd class="mt-1 text-ink-950">{ACTION_LABELS[selected.action] ?? selected.action}</dd>
			</div>
			<div>
				<dt class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">Ressource concernée</dt>
				<dd class="mt-1 text-ink-950">{resourceLabel(selected)}</dd>
			</div>
			<div>
				<dt class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">Adresse IP</dt>
				<dd class="mt-1 text-ink-950">{selected.ip_address ?? '—'}</dd>
			</div>
			<div>
				<dt class="text-xs font-medium tracking-wide text-ink-800/50 uppercase">Métadonnées</dt>
				{#if selected.details && Object.keys(selected.details).length > 0}
					<dd class="mt-2 flex flex-col gap-1.5 rounded-input bg-paper-100 p-3">
						{#each Object.entries(selected.details) as [key, value] (key)}
							<div class="flex justify-between gap-4 text-xs">
								<span class="text-ink-800/60">{key}</span>
								<span class="text-right font-medium text-ink-950">{String(value)}</span>
							</div>
						{/each}
					</dd>
				{:else}
					<dd class="mt-1 text-ink-800/50">Aucune</dd>
				{/if}
			</div>
		</dl>
	{/if}
</Drawer>
