<script lang="ts">
	import { EnvelopeSimple } from 'phosphor-svelte';
	import { apiCall, ApiError } from '@iumc/api';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';
	import AuthCard from '$lib/AuthCard.svelte';

	let email = $state('');
	let sent = $state(false);
	let error = $state('');
	let submitting = $state(false);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		submitting = true;
		error = '';
		try {
			await apiCall('/auth/forgot-password', { method: 'POST', body: { email } });
			sent = true;
		} catch (exception) {
			error = exception instanceof ApiError ? exception.message : 'Envoi impossible.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Mot de passe oublié, panel IUMC</title>
</svelte:head>

<AuthCard>
	<div class="flex items-center gap-3">
		<img src="/logo-iumc-embleme.png" alt="" class="h-12 w-auto" />
		<img src="/logo-iumc-wordmark.png" alt="IUMC" class="h-6 w-auto" />
	</div>
	<h1 class="mt-4 text-lg font-medium text-ink-800">Mot de passe oublié</h1>

	{#if sent}
		<p class="mt-8 rounded-input bg-green-500/10 px-4 py-3 text-sm text-green-600">
			Si un compte existe avec cette adresse, un e-mail contenant un lien de
			réinitialisation (valable 1 heure) vient de lui être envoyé.
		</p>
		<a href="/admin/login" class="mt-6 text-center text-sm text-ink-800/70 hover:text-ink-950">
			Retour à la connexion
		</a>
	{:else}
		<form class="mt-8 flex flex-col gap-4" onsubmit={submit}>
			<TextField id="email" label="Adresse e-mail" type="email" icon={EnvelopeSimple} required bind:value={email} />
			{#if error}
				<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">{error}</p>
			{/if}
			<button type="submit" disabled={submitting}
				class="mt-2 rounded-pill bg-green-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-green-600 disabled:opacity-60">
				{submitting ? 'Envoi…' : 'Envoyer le lien'}
			</button>
			<a href="/admin/login" class="text-center text-xs text-ink-800/60 hover:text-ink-900">Retour à la connexion</a>
		</form>
	{/if}
</AuthCard>
