<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import { getStoredBatchIds } from '$lib/storage';
	import { getBatch, getCompiledPdfUrl, type BatchMeta } from '$lib/api';

	let batchIds = $state<string[]>([]);
	let batches = $state<Record<string, BatchMeta | null>>({});
	let loading = $state(true);

	onMount(() => {
		batchIds = getStoredBatchIds();
		loading = false;
		batchIds.forEach((id) => fetchBatch(id));
	});

	async function fetchBatch(id: string) {
		try {
			const b = await getBatch(id);
			batches = { ...batches, [id]: b };
		} catch {
			batches = { ...batches, [id]: null };
		}
	}
</script>

<div>
	<h1 class="mb-6 text-2xl font-semibold">Your processed batches</h1>

	{#if loading}
		<p class="text-muted-foreground">Loading...</p>
	{:else if batchIds.length === 0}
		<Card.Root class="border-dashed">
			<Card.Content class="flex flex-col items-center justify-center py-12">
				<p class="mb-4 text-muted-foreground">No batches yet.</p>
				<Button href="/process">Process your first PDFs</Button>
			</Card.Content>
		</Card.Root>
	{:else}
		<div class="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
			{#each batchIds as id}
				{@const b = batches[id]}
				<Card.Root class="transition-shadow hover:shadow-md">
					<Card.Header class="flex flex-row items-start justify-between space-y-0">
						<Card.Title class="text-base">
							{b?.name ?? id.slice(0, 8)}
						</Card.Title>
						{#if b}
							<Badge
								variant={
									b.status === 'completed' || b.status === 'completed_with_errors'
										? 'default'
										: b.status === 'failed'
											? 'destructive'
											: 'secondary'
								}
							>
								{b.status}
							</Badge>
						{:else}
							<Badge variant="outline">...</Badge>
						{/if}
					</Card.Header>
					<Card.Content>
						{#if b}
							<p class="text-sm text-muted-foreground">
								{b.pdf_count} PDF(s): {b.pdf_names?.slice(0, 2).join(', ')}
								{#if (b.pdf_names?.length ?? 0) > 2}
									...
								{/if}
							</p>
						{:else}
							<p class="text-sm text-muted-foreground">Loading...</p>
						{/if}
					</Card.Content>
					<Card.Footer class="flex gap-2">
						<Button href="/batches/{id}" variant="outline" size="sm">
							View
						</Button>
						{#if b && (b.status === 'completed' || b.status === 'completed_with_errors') && b.compiled_pdf}
							<Button href={getCompiledPdfUrl(id)} variant="default" size="sm" target="_blank">
								Download PDF
							</Button>
						{/if}
					</Card.Footer>
				</Card.Root>
			{/each}
		</div>
	{/if}
</div>
