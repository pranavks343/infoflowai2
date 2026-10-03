export default function (component) {
  const { parentElement, data, setStateValue } = component;
  const status = parentElement.querySelector('.clerk-status');
  const controls = parentElement.querySelector('.clerk-controls');
  const nodes = {
    'sign-in': parentElement.querySelector('.clerk-signin'),
    'sign-up': parentElement.querySelector('.clerk-signup'),
    'signed-in': parentElement.querySelector('.clerk-user'),
  };
  let disposed = false;
  let clerk;
  let unsubscribe;
  let timer;
  let mode;
  let lastToken = window.infoflowLastToken;

  function loadScript(src, key) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.crossOrigin = 'anonymous';
      if (key) script.dataset.clerkPublishableKey = key;
      script.onload = resolve;
      script.onerror = () => reject(new Error('Could not load Clerk'));
      document.head.appendChild(script);
    });
  }

  function unmount() {
    if (!clerk) return;
    if (mode === 'sign-in') clerk.unmountSignIn(nodes[mode]);
    if (mode === 'sign-up') clerk.unmountSignUp(nodes[mode]);
    if (mode === 'signed-in') clerk.unmountUserButton(nodes[mode]);
  }

  function mount(nextMode) {
    if (disposed || mode === nextMode) return;
    unmount();
    mode = nextMode;
    controls.replaceChildren();
    for (const [name, node] of Object.entries(nodes)) node.hidden = name !== nextMode;
    const widget = nodes[nextMode];
    status.textContent = '';
    if (nextMode === 'signed-in') {
      clerk.mountUserButton(widget, { signOutRedirectUrl: location.origin + '/' });
      return;
    }
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = nextMode === 'sign-in' ? 'Create an account' : 'Already have an account? Sign in';
    button.style.cssText = 'margin:12px 0;padding:8px 12px;cursor:pointer;background:white;border:1px solid #ddd;border-radius:8px;';
    button.onclick = () => mount(nextMode === 'sign-in' ? 'sign-up' : 'sign-in');
    controls.appendChild(button);
    const options = {
      routing: 'hash',
      signInFallbackRedirectUrl: location.origin + '/',
      signUpFallbackRedirectUrl: location.origin + '/',
    };
    if (nextMode === 'sign-up') clerk.mountSignUp(widget, options);
    else clerk.mountSignIn(widget, options);
  }

  async function sync() {
    if (disposed) return;
    if (!clerk.session) {
      if (mode !== 'sign-up') mount('sign-in');
      if (lastToken != null) {
        lastToken = null;
        window.infoflowLastToken = null;
        setStateValue('auth', null);
      }
      return;
    }
    mount('signed-in');
    const session = clerk.session;
    const token = await session.getToken();
    if (disposed || clerk.session?.id !== session.id) return;
    if (token !== lastToken) {
      lastToken = token;
      window.infoflowLastToken = token;
      setStateValue('auth', {
        token,
        name: clerk.user?.fullName || clerk.user?.primaryEmailAddress?.emailAddress || '',
      });
    }
  }

  (async () => {
    try {
      const key = data.publishableKey;
      const domain = atob(key.split('_')[2]).replace(/\$$/, '');
      if (!/^[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$/.test(domain)) throw new Error('Invalid Clerk domain');
      if (!window.infoflowClerkPromise) {
        window.infoflowClerkPromise = (async () => {
          await loadScript(`https://${domain}/npm/@clerk/ui@1/dist/ui.browser.js`);
          await loadScript(`https://${domain}/npm/@clerk/clerk-js@6/dist/clerk.browser.js`, key);
          await window.Clerk.load({ ui: { ClerkUI: window.__internal_ClerkUICtor } });
          return window.Clerk;
        })().catch(error => {
          delete window.infoflowClerkPromise;
          throw error;
        });
      }
      clerk = await window.infoflowClerkPromise;
      if (disposed) return;
      unsubscribe = clerk.addListener(() => { sync().catch(fail); });
      await sync();
      timer = setInterval(() => { sync().catch(fail); }, 20000);
    } catch (error) { fail(error); }
  })();

  function fail(error) {
    if (disposed) return;
    status.textContent = 'Unable to load secure sign-in. Please refresh and try again.';
    lastToken = null;
    window.infoflowLastToken = null;
    setStateValue('auth', { token: null, error: true });
  }

  return () => {
    disposed = true;
    clearInterval(timer);
    if (unsubscribe) unsubscribe();
    unmount();
  };
}
