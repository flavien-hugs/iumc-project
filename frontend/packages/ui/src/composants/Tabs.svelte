<script lang="ts">
	let {
		tabs,
		active = $bindable()
	}: {
		tabs: { id: string; label: string }[];
		active: string;
	} = $props();

	function onKeydown(event: KeyboardEvent, index: number) {
		if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
		event.preventDefault();
		const delta = event.key === 'ArrowRight' ? 1 : -1;
		const next = tabs[(index + delta + tabs.length) % tabs.length];
		active = next.id;
		const el = document.getElementById(`tab-${next.id}`);
		el?.focus();
	}
</script>

<div role="tablist" class="flex flex-wrap gap-x-6 gap-y-2 border-b border-ink-900/10">
	{#each tabs as tab, i (tab.id)}
		<button
			id={`tab-${tab.id}`}
			type="button"
			role="tab"
			aria-selected={active === tab.id}
			tabindex={active === tab.id ? 0 : -1}
			onclick={() => (active = tab.id)}
			onkeydown={(event) => onKeydown(event, i)}
			class={`group relative pb-3 text-sm transition-colors ${
				active === tab.id ? 'font-medium text-gold-600' : 'text-ink-800 hover:text-gold-600'
			}`}
		>
			{tab.label}
			<span
				class={`absolute -bottom-px left-0 h-[2px] w-full origin-left bg-gold-500 transition-transform duration-300 ${
					active === tab.id ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'
				}`}
			></span>
		</button>
	{/each}
</div>
