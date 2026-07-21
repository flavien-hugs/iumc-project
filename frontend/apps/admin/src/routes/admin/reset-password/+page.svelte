<script lang="ts">
	import { LockKey } from 'phosphor-svelte';
	import { page } from '$app/state';
	import { apiCall, ApiError } from '@iumc/api';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';

	const token = page.url.searchParams.get('token') ?? '';

	let password = $state('');
	let done = $state(false);
	let error = $state('');
	let submitting = $state(false);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		error = '';
		try {
			await apiCall('/auth/reset-password', {
				method: 'POST',
				body: { token, new_password: password }
			});
			done = true;
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Réinitialisation impossible.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Nouveau mot de passe, panel IUMC</title>
</svelte:head>

<div class="mx-auto flex min-h-dvh max-w-sm flex-col justify-center px-6">
	<p class="font-display text-3xl font-semibold text-ink-950">IUMC</p>
	<h1 class="mt-1 text-lg font-medium text-ink-800">Nouveau mot de passe</h1>

	{#if !token}
		<p class="mt-8 rounded-input bg-ink-900/5 px-4 py-3 text-sm text-ink-900">
			Lien invalide. Refaites une demande depuis « Mot de passe oublié ».
		</p>
	{:else if done}
		<p class="mt-8 rounded-input bg-gold-500/10 px-4 py-3 text-sm text-gold-600">
			Mot de passe mis à jour. Vous pouvez vous connecter.
		</p>
		<a href="/admin/login" class="mt-6 rounded-pill bg-gold-500 px-5 py-2.5 text-center text-sm font-medium text-ink-950 hover:bg-gold-600">
			Se connecter
		</a>
	{:else}
		<form class="mt-8 flex flex-col gap-4" onsubmit={submit}>
			<TextField id="mot-de-passe" label="Nouveau mot de passe (10 caractères min.)" type="password" icon={LockKey} required minlength={10} bind:value={password} />
			{#if error}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
			{/if}
			<button type="submit" disabled={submitting}
				class="mt-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60">
				{submitting ? 'Enregistrement…' : 'Définir le mot de passe'}
			</button>
		</form>
	{/if}
</div>
