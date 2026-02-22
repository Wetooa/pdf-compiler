<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import favicon from '$lib/assets/favicon.svg';
	import { Button } from '$lib/components/ui/button';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="min-h-screen bg-background text-foreground">
	<header class="border-b border-border">
		<nav class="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
			<a href="/" class="text-xl font-semibold">PDF Compiler</a>
			<div class="flex gap-2">
				<Button href="/" variant={$page.url.pathname === '/' ? 'default' : 'ghost'} size="sm">
					Home
				</Button>
				<Button href="/process" variant={$page.url.pathname === '/process' ? 'default' : 'ghost'} size="sm">
					Process new
				</Button>
			</div>
		</nav>
	</header>
	<main class="mx-auto max-w-4xl px-4 py-8">
		{@render children()}
	</main>
</div>
