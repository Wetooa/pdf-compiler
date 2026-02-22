<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as Card from '$lib/components/ui/card';
	import { createBatch } from '$lib/api';
	import { addBatchId } from '$lib/storage';

	let files = $state<File[]>([]);
	let name = $state('');
	let uploading = $state(false);
	let error = $state('');

	let fileInput: HTMLInputElement;

	function onFileChange(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files) {
			const list = Array.from(target.files).filter((f) => f.name.toLowerCase().endsWith('.pdf'));
			files = list;
		}
	}

	function removeFile(index: number) {
		files = files.filter((_, i) => i !== index);
	}

	async function submit() {
		if (files.length === 0) {
			error = 'Please select at least one PDF file.';
			return;
		}
		error = '';
		uploading = true;
		try {
			const batch = await createBatch(files, name || undefined);
			addBatchId(batch.id);
			goto(`/batches/${batch.id}`);
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Upload failed';
		} finally {
			uploading = false;
		}
	}
</script>

<div>
	<h1 class="mb-6 text-2xl font-semibold">Process PDFs</h1>

	<Card.Root class="max-w-xl">
		<Card.Header>
			<Card.Title>Upload PDFs</Card.Title>
			<Card.Description>
				Select one or more PDF files. They will be processed and compiled into a single learning guide PDF.
			</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			<div>
				<label for="batch-name" class="mb-2 block text-sm font-medium">Batch name (optional)</label>
				<Input id="batch-name" type="text" bind:value={name} placeholder="e.g. Semester 2 - Math" />
			</div>

			<div>
				<label for="pdf-files" class="mb-2 block text-sm font-medium">PDF files</label>
				<input
					id="pdf-files"
					bind:this={fileInput}
					type="file"
					accept=".pdf"
					multiple
					class="hidden"
					onchange={onFileChange}
				/>
				<Button
					type="button"
					variant="outline"
					onclick={() => fileInput?.click()}
					class="w-full border-dashed"
				>
					Choose PDFs
				</Button>
				{#if files.length > 0}
					<ul class="mt-2 space-y-1 text-sm">
						{#each files as f, i}
							<li class="flex items-center justify-between rounded bg-muted/50 px-2 py-1">
								<span class="truncate">{f.name}</span>
								<Button type="button" variant="ghost" size="icon-sm" onclick={() => removeFile(i)}>
									×
								</Button>
							</li>
						{/each}
					</ul>
				{/if}
			</div>

			{#if error}
				<p class="text-sm text-destructive">{error}</p>
			{/if}
		</Card.Content>
		<Card.Footer>
			<Button onclick={submit} disabled={uploading || files.length === 0}>
				{uploading ? 'Uploading...' : 'Process PDFs'}
			</Button>
		</Card.Footer>
	</Card.Root>
</div>
