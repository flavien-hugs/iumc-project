<script lang="ts">
	import {
		Buildings,
		CheckCircle,
		Clock,
		EnvelopeSimple,
		Eye,
		FloppyDisk,
		FunnelSimple,
		House,
		MagnifyingGlass,
		MapPin,
		MapPinLine,
		Phone,
		Plus,
		Signpost,
		Trash,
		UserCircle,
		WhatsappLogo
	} from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { page } from '$app/state';
	import { apiCall, ApiError } from '@iumc/api';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import ConfirmDialog from '@iumc/ui/composants/ConfirmDialog.svelte';
	import Toolbar from '@iumc/ui/composants/Toolbar.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import SearchSelect from '@iumc/ui/formulaire/SearchSelect.svelte';
	import RichTextEditor from '@iumc/ui/formulaire/RichTextEditor.svelte';
	import { LOCATION_STATUS_LABELS, formatDateTime } from '$lib/labels';
	import type { LocationRow } from './+page';
	import type { PageProps } from './$types';

	const statusFormOptions = Object.entries(LOCATION_STATUS_LABELS).map(([value, label]) => ({
		value,
		label
	}));
	const statusOptions = [{ value: '', label: 'Tous les statuts' }, ...statusFormOptions];

	let { data }: PageProps = $props();
	const locationsPage = $derived(data.locationsPage);

	let searchText = $state(data.q);
	let statusValue = $state(data.status);
	let refreshing = $state(false);

	function applyFilters(overrides: Record<string, string> = {}) {
		const params = new URLSearchParams();
		const q = overrides.q ?? searchText;
		const status = overrides.status ?? statusValue;
		if (q.trim()) params.set('q', q.trim());
		if (status) params.set('status', status);
		goto(`/admin/locations${params.size > 0 ? `?${params}` : ''}`, { keepFocus: true });
	}

	function resetFilters() {
		searchText = '';
		statusValue = '';
		applyFilters({ q: '', status: '' });
	}

	async function refresh() {
		refreshing = true;
		try {
			await invalidateAll();
		} finally {
			refreshing = false;
		}
	}

	const hasActiveFilters = $derived(Boolean(data.q || data.status));

	type LocationForm = {
		name: string;
		city: string;
		district: string;
		address: string;
		latitude: number | null;
		longitude: number | null;
		status: string;
		phone: string;
		whatsapp: string;
		email: string;
		opening_hours: string;
		manager_name: string;
		description: string;
		is_visible: boolean;
	};

	const EMPTY: LocationForm = {
		name: '',
		city: '',
		district: '',
		address: '',
		latitude: null,
		longitude: null,
		status: 'planned',
		phone: '',
		whatsapp: '',
		email: '',
		opening_hours: '',
		manager_name: '',
		description: '',
		is_visible: true
	};

	let drawerOpen = $state(false);
	let editingId = $state<number | null>(null);
	let form = $state({ ...EMPTY });
	let saving = $state(false);
	let error = $state('');

	function openCreate() {
		editingId = null;
		form = { ...EMPTY };
		error = '';
		drawerOpen = true;
	}

	function openEdit(location: LocationRow) {
		editingId = location.id;
		form = {
			name: location.name,
			city: location.city,
			district: location.district ?? '',
			address: location.address ?? '',
			latitude: location.latitude,
			longitude: location.longitude,
			status: location.status,
			phone: location.phone ?? '',
			whatsapp: location.whatsapp ?? '',
			email: location.email ?? '',
			opening_hours: location.opening_hours ?? '',
			manager_name: location.manager_name ?? '',
			description: location.description ?? '',
			is_visible: location.is_visible
		};
		error = '';
		drawerOpen = true;
	}

	function closeDrawer() {
		drawerOpen = false;
	}

	async function save(event: SubmitEvent) {
		event.preventDefault();
		saving = true;
		error = '';
		const payload = {
			name: form.name,
			city: form.city,
			district: form.district || null,
			address: form.address || null,
			latitude: form.latitude,
			longitude: form.longitude,
			status: form.status,
			phone: form.phone || null,
			whatsapp: form.whatsapp || null,
			email: form.email || null,
			opening_hours: form.opening_hours || null,
			manager_name: form.manager_name || null,
			description: form.description || null,
			is_visible: form.is_visible
		};
		try {
			if (editingId === null) {
				await apiCall('/admin/locations', { method: 'POST', body: payload });
			} else {
				await apiCall(`/admin/locations/${editingId}`, { method: 'PATCH', body: payload });
			}
			drawerOpen = false;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			saving = false;
		}
	}

	let deleteTargetId = $state<number | null>(null);
	let deleteLoading = $state(false);
	let deleteError = $state('');

	function requestDelete(id: number, event?: MouseEvent) {
		event?.stopPropagation();
		deleteTargetId = id;
		deleteError = '';
	}

	async function confirmDelete() {
		if (deleteTargetId === null) return;
		deleteLoading = true;
		deleteError = '';
		try {
			await apiCall(`/admin/locations/${deleteTargetId}`, { method: 'DELETE' });
			deleteTargetId = null;
			drawerOpen = false;
			await invalidateAll();
		} catch (exception) {
			deleteError = exception instanceof ApiError ? exception.message : 'Suppression impossible.';
		} finally {
			deleteLoading = false;
		}
	}

	function changePage(nextPage: number) {
		const params = new URLSearchParams(page.url.searchParams);
		params.set('page', String(nextPage));
		goto(`/admin/locations?${params}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Implantations, panel IUMC</title>
</svelte:head>

<div>
	<h1 class="text-3xl font-semibold text-ink-950">Implantations</h1>
	<p class="mt-2 text-sm text-ink-800/70">Siège et villes d'expansion affichées sur le site.</p>
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
			<div class="w-72">
				<TextField
					id="q"
					label="Recherche"
					icon={MagnifyingGlass}
					placeholder="Nom, ville, quartier…"
					bind:value={searchText}
					compact
				/>
			</div>
			<div class="w-56">
				<SearchSelect
					id="status-filter"
					label="Statut"
					icon={CheckCircle}
					options={statusOptions}
					bind:value={statusValue}
					onchange={() => applyFilters()}
					compact
				/>
			</div>
			<button
				type="submit"
				class="inline-flex items-center gap-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600"
			>
				<FunnelSimple size={16} />
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
	{#snippet primaryAction()}
		<button
			type="button"
			onclick={openCreate}
			class="inline-flex items-center gap-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600"
		>
			<Plus size={16} />
			Ajouter une implantation
		</button>
	{/snippet}
</Toolbar>

{#if locationsPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<MapPinLine size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucune implantation pour le moment</p>
	</div>
{:else}
	<div class="mt-8 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
		<table class="w-full min-w-160 text-left text-sm">
			<thead>
				<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
					<th class="px-4 py-3 font-medium">#</th>
					<th class="px-4 py-3 font-medium">Ville</th>
					<th class="px-4 py-3 font-medium">Statut</th>
					<th class="px-4 py-3 font-medium">Téléphone</th>
					<th class="px-4 py-3 font-medium">Visible</th>
					<th class="px-4 py-3 font-medium">Mise à jour</th>
					<th class="px-4 py-3 font-medium">Actions</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-ink-900/5">
				{#each locationsPage.items as location, i (location.id)}
					<tr class="cursor-pointer hover:bg-ink-900/4" onclick={() => openEdit(location)}>
						<td class="px-4 py-3 text-ink-800/50 tabular-nums">
							{(locationsPage.page - 1) * locationsPage.page_size + i + 1}
						</td>
						<td class="px-4 py-3">
							<span class="block font-medium text-ink-950">{location.name}</span>
							<span class="block text-xs text-ink-800/60">{location.city}</span>
						</td>
						<td class="px-4 py-3">
							<span
								class={`rounded-pill px-2.5 py-1 text-xs font-medium ${location.status === 'headquarters' ? 'bg-green-500/15 text-green-600' : 'bg-ink-900/5 text-ink-800/70'}`}
							>
								{LOCATION_STATUS_LABELS[location.status] ?? location.status}
							</span>
						</td>
						<td class="px-4 py-3 text-ink-800">{location.phone ?? '-'}</td>
						<td class="px-4 py-3 text-ink-800">{location.is_visible ? 'Oui' : 'Non'}</td>
						<td class="px-4 py-3 whitespace-nowrap text-ink-800/70">
							{formatDateTime(location.updated_at)}
						</td>
						<td class="px-4 py-3">
							<div class="flex items-center gap-1">
								<button
									type="button"
									title="Voir le détail"
									aria-label="Voir le détail"
									onclick={(event) => {
										event.stopPropagation();
										openEdit(location);
									}}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<Eye size={16} />
								</button>
								<button
									type="button"
									title="Supprimer"
									aria-label="Supprimer"
									onclick={(event) => requestDelete(location.id, event)}
									class="rounded-input p-1.5 text-ink-800/60 hover:bg-ink-900/5 hover:text-ink-950"
								>
									<Trash size={16} />
								</button>
							</div>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<Pagination
		page={locationsPage.page}
		pageSize={locationsPage.page_size}
		total={locationsPage.total}
		onchange={changePage}
	/>
{/if}

<Drawer
	open={drawerOpen}
	title={editingId === null ? 'Ajouter une implantation' : "Modifier l'implantation"}
	onclose={closeDrawer}
>
	<form class="flex flex-col gap-4" onsubmit={save}>
		<div class="grid gap-4 sm:grid-cols-2">
			<TextField id="loc-name" label="Nom" icon={Buildings} required bind:value={form.name} />
			<TextField id="loc-city" label="Ville" icon={MapPin} required bind:value={form.city} />
		</div>

		<div class="grid gap-4 sm:grid-cols-2">
			<TextField id="loc-district" label="Commune / quartier" icon={Signpost} bind:value={form.district} />
			<SearchSelect
				id="loc-status"
				label="Statut"
				icon={CheckCircle}
				options={statusFormOptions}
				required
				bind:value={form.status}
			/>
		</div>

		<TextField id="loc-address" label="Adresse" icon={House} bind:value={form.address} />

		<div class="grid gap-4 sm:grid-cols-2">
			<TextField id="loc-phone" label="Téléphone" icon={Phone} bind:value={form.phone} />
			<TextField id="loc-whatsapp" label="WhatsApp" icon={WhatsappLogo} bind:value={form.whatsapp} />
		</div>

		<div class="grid gap-4 sm:grid-cols-2">
			<TextField id="loc-email" label="E-mail" type="email" icon={EnvelopeSimple} bind:value={form.email} />
			<TextField
				id="loc-hours"
				label="Horaires"
				icon={Clock}
				placeholder="Du lundi au vendredi, 8h-17h"
				bind:value={form.opening_hours}
			/>
		</div>

		<TextField id="loc-manager" label="Responsable" icon={UserCircle} bind:value={form.manager_name} />

		<RichTextEditor
			id="loc-description"
			label="Description"
			bind:value={form.description}
			placeholder="Présentation de l'implantation…"
		/>

		<label class="flex items-center gap-2 text-sm text-ink-800">
			<input type="checkbox" bind:checked={form.is_visible} class="accent-green-500" />
			Visible sur le site public
		</label>

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
		{/if}

		<div class="mt-2 flex items-center justify-between gap-3">
			<button
				type="submit"
				disabled={saving}
				class="inline-flex items-center gap-2 rounded-pill bg-green-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60"
			>
				{#if editingId === null}
					<Plus size={16} />
					Créer
				{:else}
					<FloppyDisk size={16} />
					Enregistrer
				{/if}
			</button>
			{#if editingId !== null}
				<button
					type="button"
					onclick={() => requestDelete(editingId as number)}
					class="inline-flex items-center gap-2 rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-800/70 hover:border-ink-900/40"
				>
					<Trash size={14} />
					Supprimer
				</button>
			{/if}
		</div>
	</form>
</Drawer>

<ConfirmDialog
	open={deleteTargetId !== null}
	title="Supprimer cette implantation ?"
	description="Cette action est définitive et retire l'implantation du site public."
	confirmLabel="Supprimer"
	destructive
	loading={deleteLoading}
	error={deleteError}
	onconfirm={confirmDelete}
	oncancel={() => (deleteTargetId = null)}
/>
