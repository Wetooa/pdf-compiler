<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { getBatch, getCompiledPdfUrl, type BatchMeta } from '$lib/api';
	import { addBatchId } from '$lib/storage';

	const batchId = $derived($page.params.id);
	let batch = $state<BatchMeta | null>(null);
	let loading = $state(true);
	let error = $state('');

	onMount(() => {
		addBatchId(batchId);
		poll();
	});

	async function poll() {
		loading = true;
		error = '';
		try {
			const b = await getBatch(batchId);
			batch = b;
			loading = false;
			if (b.status === 'processing') {
				setTimeout(poll, 3000);
			}
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Failed to load batch';
			loading = false;
		}
	}

</script>

<div>
	<a href="/" class="mb-4 inline-block text-sm text-muted-foreground hover:underline">← Back to batches</a>

	{#if error}
		<Card.Root class="border-destructive">
			<Card.Content class="py-6">
				<p class="text-destructive">{error}</p>
			</Card.Content>
		</Card.Root>
	{:else if loading && !batch}
		<p class="text-muted-foreground">Loading...</p>
	{:else if batch}
		<h1 class="mb-6 text-2xl font-semibold">{batch.name}</h1>

		<Card.Root class="mb-6">
			<Card.Header class="flex flex-row items-center justify-between">
				<Card.Title>Status</Card.Title>
				<Badge
					variant={
						batch.status === 'completed' || batch.status === 'completed_with_errors'
							? 'default'
							: batch.status === 'failed'
								? 'destructive'
								: 'secondary'
					}
				>
					{batch.status}
				</Badge>
			</Card.Header>
			<Card.Content>
				{#if batch.status === 'processing'}
					<p class="text-muted-foreground">
						Processing {batch.pdf_count} PDF(s)... This may take several minutes.
					</p>
					<p class="mt-2 text-sm text-muted-foreground">Page will refresh automatically.</p>
				{:else if batch.status === 'failed' && batch.error}
					<p class="text-destructive">{batch.error}</p>
				{:else if batch.status === 'completed' || batch.status === 'completed_with_errors'}
					<p class="text-muted-foreground">
						{batch.pdf_count} PDF(s) processed.
						{batch.failed_count ? ` ${batch.failed_count} failed.` : ''}
					</p>
				{/if}
			</Card.Content>
		</Card.Root>

		{#if batch.pdf_names && batch.pdf_names.length > 0}
			<h2 class="mb-2 text-lg font-medium">PDFs in this batch</h2>
			<ul class="mb-6 list-disc space-y-1 pl-6 text-sm text-muted-foreground">
				{#each batch.pdf_names as pdfName}
					<li>{pdfName}</li>
				{/each}
			</ul>
		{/if}

		{#if (batch.status === 'completed' || batch.status === 'completed_with_errors') && batch.compiled_pdf}
			<Card.Root>
				<Card.Header>
					<Card.Title>Download</Card.Title>
					<Card.Description>Your compiled learning guide PDF is ready.</Card.Description>
				</Card.Header>
				<Card.Footer>
					<Button href={getCompiledPdfUrl(batchId)} target="_blank">Download compiled PDF</Button>
				</Card.Footer>
			</Card.Root>
		{/if}
	{/if}
</div>

