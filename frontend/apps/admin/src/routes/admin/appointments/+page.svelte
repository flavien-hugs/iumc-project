<script lang="ts">
	import { CalendarBlank, Clock, NotePencil } from 'phosphor-svelte';
	import { goto, invalidateAll } from '$app/navigation';
	import { apiCall, ApiError } from '@iumc/api';
	import Pagination from '@iumc/ui/composants/Pagination.svelte';
	import Drawer from '@iumc/ui/composants/Drawer.svelte';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import TextareaField from '@iumc/ui/formulaire/TextareaField.svelte';
	import { APPOINTMENT_STATUS_LABELS, formatDate } from '$lib/labels';
	import type { AppointmentRow } from './+page';
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const appointmentsPage = $derived(data.appointmentsPage);

	let selected = $state<AppointmentRow | null>(null);
	let rescheduleDate = $state('');
	let rescheduleTime = $state('');
	let rescheduleNote = $state('');
	let saving = $state(false);
	let error = $state('');

	function openDetail(appointment: AppointmentRow) {
		selected = appointment;
		rescheduleDate = appointment.date;
		rescheduleTime = appointment.time ? appointment.time.slice(0, 5) : '';
		rescheduleNote = appointment.note ?? '';
		error = '';
	}

	async function setStatus(id: number, status: string) {
		error = '';
		try {
			await apiCall(`/admin/appointments/${id}`, { method: 'PATCH', body: { status } });
			selected = null;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Action impossible.';
		}
	}

	async function saveReschedule(event: SubmitEvent) {
		event.preventDefault();
		if (!selected) return;
		saving = true;
		error = '';
		try {
			await apiCall(`/admin/appointments/${selected.id}`, {
				method: 'PATCH',
				body: { date: rescheduleDate, time: rescheduleTime || null, note: rescheduleNote || null }
			});
			selected = null;
			await invalidateAll();
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Enregistrement impossible.';
		} finally {
			saving = false;
		}
	}

	function changePage(nextPage: number) {
		goto(`/admin/appointments?page=${nextPage}`, { keepFocus: true });
	}
</script>

<svelte:head>
	<title>Rendez-vous, panel IUMC</title>
</svelte:head>

<h1 class="text-3xl font-semibold text-ink-950">Rendez-vous</h1>
<p class="mt-2 text-sm text-ink-800/70">Les rendez-vous planifiés depuis les demandes.</p>

{#if appointmentsPage.items.length === 0}
	<div
		class="mt-8 flex flex-col items-center gap-3 rounded-card border border-ink-900/10 bg-paper-50 px-6 py-16 text-center"
	>
		<CalendarBlank size={32} class="text-ink-800/30" />
		<p class="font-medium text-ink-950">Aucun rendez-vous planifié</p>
		<p class="max-w-[42ch] text-sm text-ink-800/60">
			Planifiez un rendez-vous depuis la page de détail d'une demande.
		</p>
	</div>
{:else}
	<div class="mt-8 overflow-x-auto rounded-card border border-ink-900/10 bg-paper-50">
		<table class="w-full min-w-160 text-left text-sm">
			<thead>
				<tr class="border-b border-ink-900/10 text-xs tracking-wide text-ink-800/50 uppercase">
					<th class="px-4 py-3 font-medium">#</th>
					<th class="px-4 py-3 font-medium">Date</th>
					<th class="px-4 py-3 font-medium">Demande</th>
					<th class="px-4 py-3 font-medium">Responsable</th>
					<th class="px-4 py-3 font-medium">Statut</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-ink-900/5">
				{#each appointmentsPage.items as appointment, i (appointment.id)}
					<tr class="cursor-pointer hover:bg-ink-900/4" onclick={() => openDetail(appointment)}>
						<td class="px-4 py-3 text-ink-800/50 tabular-nums">
							{(appointmentsPage.page - 1) * appointmentsPage.page_size + i + 1}
						</td>
						<td class="px-4 py-3 whitespace-nowrap text-ink-950">
							{formatDate(appointment.date)}{appointment.time
								? ` à ${appointment.time.slice(0, 5)}`
								: ''}
						</td>
						<td class="px-4 py-3">
							<span class="font-medium text-ink-950">{appointment.request_reference}</span>
							<span class="block text-xs text-ink-800/60">{appointment.request_full_name}</span>
						</td>
						<td class="px-4 py-3 text-ink-800">{appointment.assignee_name ?? '-'}</td>
						<td class="px-4 py-3">
							<span
								class="rounded-pill bg-ink-900/5 px-2.5 py-1 text-xs font-medium whitespace-nowrap text-ink-900"
							>
								{APPOINTMENT_STATUS_LABELS[appointment.status] ?? appointment.status}
							</span>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<Pagination
		page={appointmentsPage.page}
		pageSize={appointmentsPage.page_size}
		total={appointmentsPage.total}
		onchange={changePage}
	/>
{/if}

<Drawer
	open={selected !== null}
	title={selected?.request_reference ?? 'Rendez-vous'}
	onclose={() => (selected = null)}
>
	{#if selected}
		<div class="flex flex-col gap-5">
			<dl class="grid grid-cols-2 gap-3 rounded-card bg-paper-100 p-4 text-sm">
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Demande</dt>
					<dd class="font-medium text-ink-950">
						<a href={`/admin/requests/${selected.request_id}`} class="hover:underline">
							{selected.request_reference}
						</a>
					</dd>
				</div>
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Client</dt>
					<dd class="font-medium text-ink-950">{selected.request_full_name}</dd>
				</div>
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Responsable</dt>
					<dd class="font-medium text-ink-950">{selected.assignee_name ?? 'Non affecté'}</dd>
				</div>
				<div>
					<dt class="text-xs text-ink-800/50 uppercase">Statut</dt>
					<dd class="font-medium text-ink-950">
						{APPOINTMENT_STATUS_LABELS[selected.status] ?? selected.status}
					</dd>
				</div>
			</dl>

			{#if error}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
			{/if}

			<div class="flex flex-wrap gap-2">
				{#if selected.status === 'proposed' || selected.status === 'rescheduled'}
					<button
						type="button"
						onclick={() => selected && setStatus(selected.id, 'confirmed')}
						class="rounded-pill bg-green-500 px-4 py-2 text-sm font-medium text-ink-950 hover:bg-green-600"
					>
						Confirmer
					</button>
				{/if}
				{#if selected.status === 'confirmed'}
					<button
						type="button"
						onclick={() => selected && setStatus(selected.id, 'completed')}
						class="rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-900 hover:border-ink-900/40"
					>
						Terminer
					</button>
				{/if}
				{#if selected.status !== 'cancelled' && selected.status !== 'completed'}
					<button
						type="button"
						onclick={() => selected && setStatus(selected.id, 'cancelled')}
						class="rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-800/70 hover:border-ink-900/40"
					>
						Annuler
					</button>
				{/if}
			</div>

			{#if selected.status !== 'cancelled' && selected.status !== 'completed'}
				<form class="flex flex-col gap-3 border-t border-ink-900/10 pt-5" onsubmit={saveReschedule}>
					<h3 class="text-sm font-semibold text-ink-950">Reporter le rendez-vous</h3>
					<div class="grid grid-cols-2 gap-3">
						<TextField id="reschedule-date" label="Date" type="date" icon={CalendarBlank} required bind:value={rescheduleDate} />
						<TextField id="reschedule-time" label="Heure" type="time" icon={Clock} bind:value={rescheduleTime} />
					</div>
					<TextareaField id="reschedule-note" label="Note" icon={NotePencil} rows={3} bind:value={rescheduleNote} />
					<button
						type="submit"
						disabled={saving}
						class="rounded-pill border border-ink-900/20 px-4 py-2 text-sm font-medium text-ink-900 hover:border-ink-900/40 disabled:opacity-60"
					>
						{saving ? 'Enregistrement…' : 'Reporter'}
					</button>
				</form>
			{:else if selected.note}
				<div class="border-t border-ink-900/10 pt-5">
					<h3 class="text-sm font-semibold text-ink-950">Note</h3>
					<p class="mt-1.5 text-sm text-ink-800/75">{selected.note}</p>
				</div>
			{/if}
		</div>
	{/if}
</Drawer>
