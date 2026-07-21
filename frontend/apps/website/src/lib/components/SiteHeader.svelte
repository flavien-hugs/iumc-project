<script lang="ts">
	import { CaretDown, List, X } from 'phosphor-svelte';
	import { page } from '$app/state';
	import { divisionIcon, type PublicDivision } from '$lib/content';

	const CTA_LABEL = 'Demander un accompagnement';

	const divisions = $derived((page.data.divisions ?? []) as PublicDivision[]);

	const links = [
		{ href: '/fr/implantations', label: 'Implantations' },
		{ href: '/fr/actualites', label: 'Actualités' },
		{ href: '/fr/contact', label: 'Contact' }
	];

	function isActive(href: string): boolean {
		return page.url.pathname === href || page.url.pathname.startsWith(`${href}/`);
	}

	const divisionsActive = $derived(isActive('/fr/services'));

	let mobileOpen = $state(false);
	// États distincts : le menu desktop est un panneau flottant fermé au clic
	// extérieur, l'accordéon mobile vit à l'intérieur du panneau déjà ouvert
	// et n'a pas besoin de cette logique (les mélanger referme l'accordéon
	// mobile dès le clic qui l'ouvre, le bouton n'étant pas dans divisionsMenuEl).
	let desktopDivisionsOpen = $state(false);
	let mobileDivisionsOpen = $state(false);
	let divisionsMenuEl: HTMLDivElement | undefined = $state();

	function onDocumentClick(event: MouseEvent) {
		if (divisionsMenuEl && !divisionsMenuEl.contains(event.target as Node)) {
			desktopDivisionsOpen = false;
		}
	}

	function onDocumentKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') desktopDivisionsOpen = false;
	}

	$effect(() => {
		if (!desktopDivisionsOpen) return;
		// Attache l'écouteur au tick suivant : sinon, sur le même clic qui
		// ouvre le menu, l'évènement continue de remonter jusqu'à document
		// et se fait intercepter par ce nouvel écouteur, refermant le menu
		// aussitôt ouvert.
		const timeoutId = setTimeout(() => {
			document.addEventListener('click', onDocumentClick);
			document.addEventListener('keydown', onDocumentKeydown);
		}, 0);
		return () => {
			clearTimeout(timeoutId);
			document.removeEventListener('click', onDocumentClick);
			document.removeEventListener('keydown', onDocumentKeydown);
		};
	});

	function closeAll() {
		mobileOpen = false;
		desktopDivisionsOpen = false;
		mobileDivisionsOpen = false;
	}
</script>

<header class="sticky top-0 z-40 border-b border-ink-900/10 bg-paper-50/95 backdrop-blur-sm">
	<div class="mx-auto flex h-18 max-w-7xl items-center justify-between px-6 lg:px-10">
		<a href="/fr" class="font-display text-2xl font-semibold tracking-tight text-ink-950">
			IUMC
		</a>

		<nav class="hidden items-center gap-8 md:flex" aria-label="Navigation principale">
			{#snippet navUnderline(active: boolean)}
				<span
					class={`absolute -bottom-1.5 left-0 h-[1.5px] w-full origin-left bg-gold-500 transition-transform duration-300 ${active ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'}`}
				></span>
			{/snippet}

			<a
				href="/fr/qui-sommes-nous"
				class={`group relative text-sm transition-colors ${isActive('/fr/qui-sommes-nous') ? 'font-medium text-gold-600' : 'text-ink-800 hover:text-gold-600'}`}
			>
				Qui sommes-nous
				{@render navUnderline(isActive('/fr/qui-sommes-nous'))}
			</a>

			<div
				class="relative"
				bind:this={divisionsMenuEl}
			>
				<button
					type="button"
					class={`group relative flex items-center gap-1 text-sm transition-colors ${desktopDivisionsOpen || divisionsActive ? 'font-medium text-gold-600' : 'text-ink-800 hover:text-gold-600'}`}
					aria-expanded={desktopDivisionsOpen}
					aria-haspopup="true"
					onclick={() => (desktopDivisionsOpen = !desktopDivisionsOpen)}
				>
					Nos pôles
					<CaretDown size={14} class={`transition-transform ${desktopDivisionsOpen ? 'rotate-180' : ''}`} />
					{@render navUnderline(desktopDivisionsOpen || divisionsActive)}
				</button>

				{#if desktopDivisionsOpen}
					<div
						class="absolute top-full left-1/2 mt-3 w-72 -translate-x-1/2 rounded-card border border-ink-900/10 bg-paper-50 p-2 shadow-lg shadow-ink-950/10"
						role="menu"
					>
						<a
							href="/fr/services"
							class="block rounded-input px-3 py-2 text-sm font-medium text-ink-950 hover:bg-ink-900/5"
							onclick={() => (desktopDivisionsOpen = false)}
						>
							Tous nos pôles
						</a>
						<div class="my-1 border-t border-ink-900/10"></div>
						{#each divisions as division (division.slug)}
							{@const Icon = divisionIcon(division.slug)}
							<a
								href={`/fr/services/${division.slug}`}
								class="flex items-center gap-3 rounded-input px-3 py-2.5 hover:bg-ink-900/5"
								onclick={() => (desktopDivisionsOpen = false)}
							>
								<Icon class="h-5 w-5 shrink-0 text-ink-800/60" />
								<span class="flex-1 text-sm text-ink-900">{division.name}</span>
								{#if division.status === 'coming_soon'}
									<span
										class="rounded-pill bg-forest-600/10 px-2 py-0.5 text-[11px] font-medium text-forest-600"
									>
										Bientôt
									</span>
								{/if}
							</a>
						{/each}
					</div>
				{/if}
			</div>

			{#each links as link (link.href)}
				<a
					href={link.href}
					class={`group relative text-sm transition-colors ${isActive(link.href) ? 'font-medium text-gold-600' : 'text-ink-800 hover:text-gold-600'}`}
				>
					{link.label}
					{@render navUnderline(isActive(link.href))}
				</a>
			{/each}
		</nav>

		<a
			href="/fr/demande"
			class="hidden rounded-pill bg-gold-500 px-5 py-2.5 text-sm font-medium text-ink-950 transition-transform hover:bg-gold-600 active:scale-[0.98] sm:inline-flex"
		>
			{CTA_LABEL}
		</a>

		<button
			type="button"
			class="inline-flex items-center justify-center rounded-input p-2 text-ink-950 md:hidden"
			aria-label={mobileOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
			aria-expanded={mobileOpen}
			onclick={() => (mobileOpen = !mobileOpen)}
		>
			{#if mobileOpen}
				<X size={24} />
			{:else}
				<List size={24} />
			{/if}
		</button>
	</div>

	{#if mobileOpen}
		<nav
			class="flex flex-col gap-1 border-t border-ink-900/10 bg-paper-50 px-6 py-4 md:hidden"
			aria-label="Navigation principale mobile"
		>
			<a
				href="/fr/qui-sommes-nous"
				class={`rounded-input px-2 py-2.5 text-sm hover:bg-ink-900/5 ${isActive('/fr/qui-sommes-nous') ? 'font-medium text-gold-600' : 'text-ink-800'}`}
				onclick={closeAll}
			>
				Qui sommes-nous
			</a>

			<button
				type="button"
				class={`flex items-center justify-between rounded-input px-2 py-2.5 text-left text-sm hover:bg-ink-900/5 ${divisionsActive ? 'font-medium text-gold-600' : 'text-ink-800'}`}
				aria-expanded={mobileDivisionsOpen}
				onclick={() => (mobileDivisionsOpen = !mobileDivisionsOpen)}
			>
				Nos pôles
				<CaretDown size={14} class={`transition-transform ${mobileDivisionsOpen ? 'rotate-180' : ''}`} />
			</button>
			{#if mobileDivisionsOpen}
				<div class="ml-2 flex flex-col gap-0.5 border-l border-ink-900/10 pl-3">
					<a
						href="/fr/services"
						class="rounded-input px-2 py-2 text-sm font-medium text-ink-950 hover:bg-ink-900/5"
						onclick={closeAll}
					>
						Tous nos pôles
					</a>
					{#each divisions as division (division.slug)}
						{@const Icon = divisionIcon(division.slug)}
						<a
							href={`/fr/services/${division.slug}`}
							class="flex items-center gap-2.5 rounded-input px-2 py-2 text-sm text-ink-800 hover:bg-ink-900/5"
							onclick={closeAll}
						>
							<Icon class="h-4 w-4 shrink-0 text-ink-800/60" />
							{division.name}
							{#if division.status === 'coming_soon'}
								<span
									class="rounded-pill bg-forest-600/10 px-2 py-0.5 text-[11px] font-medium text-forest-600"
								>
									Bientôt
								</span>
							{/if}
						</a>
					{/each}
				</div>
			{/if}

			{#each links as link (link.href)}
				<a
					href={link.href}
					class={`rounded-input px-2 py-2.5 text-sm hover:bg-ink-900/5 ${isActive(link.href) ? 'font-medium text-gold-600' : 'text-ink-800'}`}
					onclick={closeAll}
				>
					{link.label}
				</a>
			{/each}
			<a
				href="/fr/demande"
				class="mt-2 rounded-pill bg-gold-500 px-5 py-2.5 text-center text-sm font-medium text-ink-950"
				onclick={closeAll}
			>
				{CTA_LABEL}
			</a>
		</nav>
	{/if}
</header>
