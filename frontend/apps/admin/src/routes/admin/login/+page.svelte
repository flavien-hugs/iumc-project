<script lang="ts">
	import { EnvelopeSimple, LockKey } from 'phosphor-svelte';
	import { goto } from '$app/navigation';
	import { apiCall, ApiError } from '@iumc/api';
	import TextField from '@iumc/ui/formulaire/TextField.svelte';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let submitting = $state(false);

	async function login(event: SubmitEvent) {
		event.preventDefault();
		error = '';
		submitting = true;
		try {
			await apiCall('/auth/login', {
				method: 'POST',
				body: { email, password }
			});
			goto('/admin');
		} catch (exception) {
			error =
				exception instanceof ApiError
					? exception.message
					: 'Connexion impossible. Vérifiez votre réseau.';
		} finally {
			submitting = false;
		}
	}
</script>

<svelte:head>
	<title>Connexion, panel IUMC</title>
</svelte:head>

<div class="mx-auto flex min-h-dvh max-w-sm flex-col justify-center px-6">
	<p class="font-display text-3xl font-semibold text-ink-950">IUMC</p>
	<h1 class="mt-1 text-lg font-medium text-ink-800">Connexion au panel</h1>

	<form class="mt-8 flex flex-col gap-4" onsubmit={login}>
		<TextField
			id="email"
			label="Adresse e-mail"
			type="email"
			icon={EnvelopeSimple}
			required
			autocomplete="username"
			bind:value={email}
		/>

		<TextField
			id="mot-de-passe"
			label="Mot de passe"
			type="password"
			icon={LockKey}
			required
			autocomplete="current-password"
			bind:value={password}
		/>

		{#if error}
			<p class="rounded-input bg-ink-900/5 px-3 py-2.5 text-sm text-ink-900" role="alert">
				{error}
			</p>
		{/if}

		<button
			type="submit"
			disabled={submitting}
			class="mt-2 rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 hover:bg-gold-600 disabled:opacity-60"
		>
			{submitting ? 'Connexion…' : 'Se connecter'}
		</button>

		<a href="/admin/forgot-password" class="text-center text-xs text-ink-800/60 hover:text-ink-900">
			Mot de passe oublié ?
		</a>
		<a href="/fr" class="text-center text-xs text-ink-800/60 hover:text-ink-900">
			Retour au site
		</a>
	</form>
</div>
