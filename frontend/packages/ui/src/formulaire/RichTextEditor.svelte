<script lang="ts">
	import { Editor } from '@tiptap/core';
	import StarterKit from '@tiptap/starter-kit';
	import Link from '@tiptap/extension-link';
	import Placeholder from '@tiptap/extension-placeholder';
	import TiptapImage from '@tiptap/extension-image';
	import {
		Image as ImageIcon,
		LinkSimple,
		ListBullets,
		ListNumbers,
		TextB,
		TextHTwo,
		TextHThree,
		TextItalic
	} from 'phosphor-svelte';

	let {
		id,
		label,
		value = $bindable(''),
		placeholder = '',
		onImageUpload
	}: {
		id: string;
		label: string;
		value?: string;
		placeholder?: string;
		/** Fournir un gestionnaire d'upload active le bouton "insérer une image"
		 * (désactivé par défaut — n'a de sens que là où c'est demandé, ex. le
		 * corps d'un article, pas une réponse de FAQ). */
		onImageUpload?: (file: File) => Promise<{ src: string; alt?: string }>;
	} = $props();

	let containerEl: HTMLDivElement | undefined = $state();
	let editor: Editor | undefined = $state();
	let focused = $state(false);
	let imageInputEl: HTMLInputElement | undefined = $state();
	let uploadingImage = $state(false);
	let imageError = $state('');

	// États des boutons de la barre d'outils, recalculés à chaque changement
	// de sélection ou de contenu (évènement "transaction" de Tiptap).
	let active = $state({ bold: false, italic: false, h2: false, h3: false, bulletList: false, orderedList: false, link: false });

	function syncActiveStates(instance: Editor) {
		active = {
			bold: instance.isActive('bold'),
			italic: instance.isActive('italic'),
			h2: instance.isActive('heading', { level: 2 }),
			h3: instance.isActive('heading', { level: 3 }),
			bulletList: instance.isActive('bulletList'),
			orderedList: instance.isActive('orderedList'),
			link: instance.isActive('link')
		};
	}

	$effect(() => {
		if (!containerEl) return;
		const instance = new Editor({
			element: containerEl,
			extensions: [
				StarterKit.configure({ heading: { levels: [2, 3] } }),
				Link.configure({ openOnClick: false, autolink: true }),
				Placeholder.configure({ placeholder }),
				...(onImageUpload ? [TiptapImage.configure({ inline: false })] : [])
			],
			content: value,
			onUpdate: ({ editor: instanceUpdate }) => {
				// Un éditeur vidé par l'utilisateur sérialise en "<p></p>" (Tiptap
				// garde toujours un paragraphe par défaut) : on ramène ça à une
				// chaîne vide pour que les `|| null` / `.trim()` côté formulaires
				// détectent correctement un champ laissé vide.
				value = instanceUpdate.isEmpty ? '' : instanceUpdate.getHTML();
			},
			onTransaction: ({ editor: instanceTransaction }) => syncActiveStates(instanceTransaction),
			onFocus: () => (focused = true),
			onBlur: () => (focused = false)
		});
		editor = instance;
		syncActiveStates(instance);
		return () => instance.destroy();
	});

	// Resynchronise le contenu si `value` change depuis l'extérieur (ex. reset
	// de formulaire à la fermeture d'un tiroir), sans boucler sur nos propres
	// mises à jour (onUpdate écrit déjà la même valeur dans l'éditeur).
	$effect(() => {
		if (editor && value !== editor.getHTML()) {
			editor.commands.setContent(value, false);
		}
	});

	function toggleLink() {
		if (!editor) return;
		if (active.link) {
			editor.chain().focus().unsetLink().run();
			return;
		}
		const url = window.prompt('Adresse du lien (https://…)');
		if (url) editor.chain().focus().setLink({ href: url }).run();
	}

	function triggerImagePicker() {
		imageInputEl?.click();
	}

	async function handleImageSelected(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		input.value = '';
		if (!file || !onImageUpload || !editor) return;
		uploadingImage = true;
		imageError = '';
		try {
			const { src, alt } = await onImageUpload(file);
			editor.chain().focus().setImage({ src, alt: alt ?? '' }).run();
		} catch (exception) {
			imageError = exception instanceof Error ? exception.message : 'Téléversement impossible.';
		} finally {
			uploadingImage = false;
		}
	}
</script>

<div class="flex flex-col gap-2">
	<span class="text-sm font-medium text-ink-900">{label}</span>
	<div
		class={`rounded-input border bg-paper-50 transition-colors ${focused ? 'border-green-500 ring-1 ring-green-500' : 'border-ink-900/20'}`}
	>
		<div class="flex flex-wrap items-center gap-0.5 border-b border-ink-900/10 p-1.5">
			<button
				type="button"
				aria-label="Gras"
				aria-pressed={active.bold}
				onclick={() => editor?.chain().focus().toggleBold().run()}
				class={`rounded-input p-1.5 ${active.bold ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<TextB size={16} />
			</button>
			<button
				type="button"
				aria-label="Italique"
				aria-pressed={active.italic}
				onclick={() => editor?.chain().focus().toggleItalic().run()}
				class={`rounded-input p-1.5 ${active.italic ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<TextItalic size={16} />
			</button>
			<span class="mx-1 h-5 w-px bg-ink-900/10"></span>
			<button
				type="button"
				aria-label="Titre de niveau 2"
				aria-pressed={active.h2}
				onclick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
				class={`rounded-input p-1.5 ${active.h2 ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<TextHTwo size={16} />
			</button>
			<button
				type="button"
				aria-label="Titre de niveau 3"
				aria-pressed={active.h3}
				onclick={() => editor?.chain().focus().toggleHeading({ level: 3 }).run()}
				class={`rounded-input p-1.5 ${active.h3 ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<TextHThree size={16} />
			</button>
			<span class="mx-1 h-5 w-px bg-ink-900/10"></span>
			<button
				type="button"
				aria-label="Liste à puces"
				aria-pressed={active.bulletList}
				onclick={() => editor?.chain().focus().toggleBulletList().run()}
				class={`rounded-input p-1.5 ${active.bulletList ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<ListBullets size={16} />
			</button>
			<button
				type="button"
				aria-label="Liste numérotée"
				aria-pressed={active.orderedList}
				onclick={() => editor?.chain().focus().toggleOrderedList().run()}
				class={`rounded-input p-1.5 ${active.orderedList ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<ListNumbers size={16} />
			</button>
			<span class="mx-1 h-5 w-px bg-ink-900/10"></span>
			<button
				type="button"
				aria-label={active.link ? 'Retirer le lien' : 'Ajouter un lien'}
				aria-pressed={active.link}
				onclick={toggleLink}
				class={`rounded-input p-1.5 ${active.link ? 'bg-ink-900/10 text-ink-950' : 'text-ink-800/70 hover:bg-ink-900/5'}`}
			>
				<LinkSimple size={16} />
			</button>
			{#if onImageUpload}
				<span class="mx-1 h-5 w-px bg-ink-900/10"></span>
				<input
					bind:this={imageInputEl}
					type="file"
					accept="image/jpeg,image/png,image/webp,image/svg+xml"
					class="hidden"
					onchange={handleImageSelected}
				/>
				<button
					type="button"
					aria-label="Insérer une image"
					onclick={triggerImagePicker}
					disabled={uploadingImage}
					class="rounded-input p-1.5 text-ink-800/70 hover:bg-ink-900/5 disabled:opacity-50"
				>
					<ImageIcon size={16} />
				</button>
			{/if}
		</div>
		<div
			bind:this={containerEl}
			id="{id}-editor"
			class="iumc-rich-text editor-content px-3 py-2.5 text-sm text-ink-950"
		></div>
	</div>
	{#if imageError}
		<p class="text-xs text-ink-900" role="alert">{imageError}</p>
	{/if}
</div>

<style>
	.editor-content :global(.tiptap) {
		outline: none;
		min-height: 8rem;
	}
	.editor-content :global(.tiptap p.is-editor-empty:first-child::before) {
		float: left;
		height: 0;
		color: color-mix(in srgb, var(--color-ink-800) 40%, transparent);
		content: attr(data-placeholder);
		pointer-events: none;
	}
	.editor-content :global(.tiptap img) {
		max-width: 100%;
		border-radius: var(--radius-input);
		margin: 0.5em 0;
	}
</style>
