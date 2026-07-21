<script lang="ts">
	import { ArrowsDownUp, CalendarBlank, Funnel, MagnifyingGlass, Tray } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { apiCall, ApiError } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import Toolbar from '@iumc/ui/composants/Toolbar.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import {
		formatDate,
		formatDateTime,
		REQUEST_STATUS_CLASSES,
		REQUEST_STATUS_LABELS
	} from '$lib/labels';
	import type { ServiceRequestSummary } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const requestsPage = $derived(data.requestsPage);

	let searchText = $state(data.q);
	let statusValue = $state(data.status);
	let dateFrom = $state(data.dateFrom);
	let dateTo = $state(data.dateTo);

	const statusOptions = [
		{ value: '', label: 'Tous les statuts' },
		...Object.entries(REQUEST_STATUS_LABELS).map(([value, label]) => ({ value, label }))
	];

	function applyFilters(overrides: Record<string, string> = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchText;
		const status = overrides.status ?? statusValue;
		const from = overrides.dateFrom ?? dateFrom;
		const to = overrides.dateTo ?? dateTo;
		const sort = overrides.sort ?? data.sort;
		if (q.trim()) params.set('q', q.trim());
		if (status) params.set('status', status);
		if (from) params.set('date_from', from);
		if (to) params.set('date_to', to);
		if (sort !== 'desc') params.set('sort', sort);
		goto(`/admin/requests${params.size > 0 ? `?${params}` : ''}`, { keepFocus: true });
	}

	function toggleSort() {
		applyFilters({ sort: data.sort === 'asc' ? 'desc' : 'asc' });
	}

	function resetFilters() {
		searchText = '';
		statusValue = '';
		dateFrom = '';
		dateTo = '';
		applyFilters({ q: '', status: '', dateFrom: '', dateTo: '' });
	}

	const hasActiveFilters = $derived(Boolean(data.q || data.status || data.dateFrom || data.dateTo));

	let refreshing = $state(false);
	async function refresh() {
		refreshing = true;
		try {
			await invalidateAll();
		} finally {
			refreshing = false;
		}
	}

	function changePage(nextPage: number) {
		const params = new URLSearchParams();
		if (data.q) params.set('q', data.q);
		if (data.status) params.set('status', data.status);
		if (data.dateFrom) params.set('date_from', data.dateFrom);
		if (data.dateTo) params.set('date_to', data.dateTo);
		if (data.sort !== 'desc') params.set('sort', data.sort);
		params.set('page', String(nextPage));
		goto(`/admin/requests?${params}`, { keepFocus: true });
	}

	// Aperçu rapide : vue condensée + changement de statut, sans quitter la
	// liste. Le détail complet (historique, rendez-vous, pièce jointe) reste
	// une page dédiée, trop riche pour un tiroir.
	let previewOpen = $state(false);
	let previewRequest = $state<ServiceRequestSummary | null>(null);
	let previewStatus = $state('');
	let previewSaving = $state(false);
	let previewError = $state('');

	function openPreview(request: ServiceRequestSummary) {
		previewRequest = request;
		previewStatus = request.status;
		previewError = '';
		previewOpen = true;
	}

	async function savePreviewStatus(event: SubmitEvent) {
		event.preventDefault();
		if (!previewRequest) return;
		previewSaving = true;
		previewError = '';
		try {
			await apiCall(`/admin/service-requests/${previewRequest.id}`, {
				method: 'PATCH',
				body: { status: previewStatus || null }
			});
			previewOpen = false;
			await invalidateAll();
		} catch (exception) {
			previewError =
				exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			previewSaving = false;
		}
	}
</script>

<svelte:head>
	<title>Demandes, panel IUMC</title>
</svelte:head>

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Demandes</h1>
		<p class="mt-2 text-sm text-ink-800/70">
			Cliquez sur une ligne pour un aperçu rapide, ou ouvrez la référence pour le détail complet.
		</p>
	</div>
</div>

<Toolbar onRefresh={refresh} {refreshing}>
	{#snippet filters()}
		<form
			class="flex flex-wrap items-end gap-3"
			onsubmit={(event) => {
				event.preventDefault();
				applyFilters();
			}}
		>
			<div class="w-64">
				<TextField
					id="q"
					label="Recherche"
					type="search"
					icon={MagnifyingGlass}
					placeholder="Référence, nom, téléphone, ville…"
					bind:value={searchText}
				/>
			</div>

			<div class="w-56">
				<SearchSelect
					id="status-filter"
					label="Statut"
					icon={Funnel}
					options={statusOptions}
					bind:value={statusValue}
					placeholder="Tous les statuts"
					onchange={() => applyFilters()}
				/>
			</div>

			<TextField id="date-from" label="Reçue depuis le" type="date" icon={CalendarBlank} bind:value={dateFrom} />
			<TextField id="date-to" label="Jusqu'au" type="date" icon={CalendarBlank} bind:value={dateTo} />

			<button
				type="submit"
				class="rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
			>
				Filtrer
			</button>
			{#if hasActiveFilters}
				<button
					type="button"
					onclick={resetFilters}
					class="rounded-pill border border-ink-900/20 px-4 py-2.5 text-sm font-medium text-ink-900 hover:border-ink-900/40"
				>
					Réinitialiser
				</button>
			{/if}
		</form>
	{/snippet}
	{#snippet actions()}
		<button
			type="button"
			onclick={toggleSort}
			title={data.sort === 'asc' ? 'Plus anciennes en premier' : 'Plus récentes en premier'}
			class="inline-flex items-center gap-2 rounded-pill border border-ink-900/20 px-4 py-2.5 text-sm font-medium text-ink-900 hover:border-ink-900/40"
		>
			<ArrowsDownUp size={16} />
			{data.sort === 'asc' ? 'Plus anciennes' : 'Plus récentes'}
		</button>
	{/snippet}
</Toolbar>

{#if requestsPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<Tray size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucune demande ne correspond à ces critères</p>
	</div>
{:else}
	<div class="mt-8 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
		<table class="w-full min-w-180 text-left text-sm">
			<thead>
				<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
					<th class="px-4 py-3 font-medium">#</th>
					<th class="px-4 py-3 font-medium">Référence</th>
					<th class="px-4 py-3 font-medium">Demandeur</th>
					<th class="px-4 py-3 font-medium">Service</th>
					<th class="px-4 py-3 font-medium">Ville</th>
					<th class="px-4 py-3 font-medium">Statut</th>
					<th class="px-4 py-3 font-medium">Reçue le</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-ink-900/5">
				{#each requestsPage.items as request, i (request.id)}
					<tr class="cursor-pointer hover:bg-ink-900/4" onclick={() => openPreview(request)}>
						<td class="px-4 py-3 text-ink-800/50 tabular-nums">
							{(requestsPage.page - 1) * requestsPage.page_size + i + 1}
						</td>
						<td class="px-4 py-3 font-medium whitespace-nowrap text-ink-950">
							{request.reference}
						</td>
						<td class="px-4 py-3">
							<span class="block text-ink-950">{request.full_name}</span>
							<span class="block text-xs text-ink-800/60">{request.phone}</span>
						</td>
						<td class="max-w-[26ch] px-4 py-3 text-ink-800">
							<span class="block truncate" title={request.service}>{request.service}</span>
							<span class="block text-xs text-ink-800/60">{request.division}</span>
						</td>
						<td class="px-4 py-3 text-ink-800">{request.city ?? '-'}</td>
						<td class="px-4 py-3">
							<span
								class={`rounded-pill px-2.5 py-1 text-xs font-medium whitespace-nowrap ${REQUEST_STATUS_CLASSES[request.status] ?? 'bg-ink-900/5 text-ink-800'}`}
							>
								{REQUEST_STATUS_LABELS[request.status] ?? request.status}
							</span>
						</td>
						<td class="px-4 py-3 whitespace-nowrap text-ink-800/70">
							{formatDate(request.created_at)}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<Pagination
		page={requestsPage.page}
		pageSize={requestsPage.page_size}
		total={requestsPage.total}
		onchange={changePage}
	/>
{/if}

<Drawer open={previewOpen} title={previewRequest?.reference ?? 'Demande'} onclose={() => (previewOpen = false)}>
	{#if previewRequest}
		<div class="flex flex-col gap-4">
			<div>
				<p class="text-lg font-semibold text-ink-950">{previewRequest.full_name}</p>
				<p class="text-sm text-ink-800/70">{previewRequest.phone}</p>
			</div>

			<dl class="grid grid-cols-2 gap-3 rounded-card bg-paper-100 p-4 text-sm">
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Service</dt>
					<dd class="font-medium text-ink-950">{previewRequest.service}</dd>
				</div>
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Pôle</dt>
					<dd class="font-medium text-ink-950">{previewRequest.division}</dd>
				</div>
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Ville</dt>
					<dd class="font-medium text-ink-950">{previewRequest.city ?? '-'}</dd>
				</div>
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Reçue le</dt>
					<dd class="font-medium text-ink-950">{formatDateTime(previewRequest.created_at)}</dd>
				</div>
			</dl>

			<form class="flex flex-col gap-3" onsubmit={savePreviewStatus}>
				<div class="flex flex-col gap-1.5">
					<label for="preview-status" class="text-sm font-medium text-ink-900">Statut</label>
					<select
						id="preview-status"
						bind:value={previewStatus}
						class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
					>
						{#each Object.entries(REQUEST_STATUS_LABELS) as [value, label] (value)}
							<option {value}>{label}</option>
						{/each}
					</select>
				</div>

				{#if previewError}
					<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
						{previewError}
					</p>
				{/if}

				<button
					type="submit"
					disabled={previewSaving}
					class="rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
				>
					Enregistrer le statut
				</button>
			</form>

			<a
				href={`/admin/requests/${previewRequest.id}`}
				class="text-center text-sm font-medium text-ink-900 underline decoration-ink-900/30 underline-offset-4 hover:decoration-ink-900"
			>
				Voir le détail complet (historique, rendez-vous, pièce jointe)
			</a>
		</div>
	{/if}
</Drawer>
