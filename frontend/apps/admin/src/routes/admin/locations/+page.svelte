<script lang="ts">
	import {
		Buildings,
		Clock,
		EnvelopeSimple,
		House,
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
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import RichTextEditor from '@iumc/ui/formulaire/RichTextEditor.svelte';
	import { LOCATION_STATUS_LABELS, formatDateTime } from '$lib/labels';
	import type { LocationRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const locationsPage = $derived(data.locationsPage);

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

	let confirmDeleteOpen = $state(false);
	let deleteLoading = $state(false);
	let deleteError = $state('');

	function requestDelete() {
		deleteError = '';
		confirmDeleteOpen = true;
	}

	async function confirmDelete() {
		if (editingId === null) return;
		deleteLoading = true;
		deleteError = '';
		try {
			await apiCall(`/admin/locations/${editingId}`, { method: 'DELETE' });
			confirmDeleteOpen = false;
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

<div class="flex flex-wrap items-center justify-between gap-4">
	<div>
		<h1 class="text-3xl font-semibold text-ink-950">Implantations</h1>
		<p class="mt-2 text-sm text-ink-800/70">Siège et villes d'expansion affichées sur le site.</p>
	</div>
	<button
		type="button"
		onclick={openCreate}
		class="inline-flex items-center gap-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600"
	>
		<Plus size={16} />
		Ajouter une implantation
	</button>
</div>

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
								class={`rounded-pill px-2.5 py-1 text-xs font-medium ${location.status === 'headquarters' ? 'bg-gold-500/15 text-gold-600' : 'bg-ink-900/5 text-ink-800/70'}`}
							>
								{LOCATION_STATUS_LABELS[location.status] ?? location.status}
							</span>
						</td>
						<td class="px-4 py-3 text-ink-800">{location.phone ?? '-'}</td>
						<td class="px-4 py-3 text-ink-800">{location.is_visible ? 'Oui' : 'Non'}</td>
						<td class="px-4 py-3 whitespace-nowrap text-ink-800/70">
							{formatDateTime(location.updated_at)}
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
			<div class="flex flex-col gap-1.5">
				<label for="loc-status" class="text-sm font-medium text-ink-900">Statut</label>
				<select
					id="loc-status"
					bind:value={form.status}
					class="rounded-input border border-ink-900/20 bg-paper-50 px-3 py-2 text-sm text-ink-950 focus:border-gold-500 focus:outline-none"
				>
					{#each Object.entries(LOCATION_STATUS_LABELS) as [value, label] (value)}
						<option {value}>{label}</option>
					{/each}
				</select>
			</div>
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
			<input type="checkbox" bind:checked={form.is_visible} class="accent-gold-500" />
			Visible sur le site public
		</label>

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
		{/if}

		<div class="mt-2 flex items-center justify-between gap-3">
			<button
				type="submit"
				disabled={saving}
				class="rounded-pill bg-gold-500 px-6 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
			>
				{editingId === null ? 'Créer' : 'Enregistrer'}
			</button>
			{#if editingId !== null}
				<button
					type="button"
					onclick={requestDelete}
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
	open={confirmDeleteOpen}
	title="Supprimer cette implantation ?"
	description="Cette action est définitive et retire l'implantation du site public."
	confirmLabel="Supprimer"
	destructive
	loading={deleteLoading}
	error={deleteError}
	onconfirm={confirmDelete}
	oncancel={() => (confirmDeleteOpen = false)}
/>
