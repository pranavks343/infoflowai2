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
  let signingOut = false;
  let authRevision = 0;

  function clearAuth() {
    authRevision += 1;
    lastToken = null;
    window.infoflowLastToken = null;
    setStateValue('auth', null);
  }

  async function signOut(button) {
    if (signingOut) return;
    signingOut = true;
    authRevision += 1;
    button.disabled = true;
    button.textContent = 'Signing out…';
    try {
      await clerk.signOut();
      clearAuth();
      // A new page also removes Streamlit's previous component/session state.
      location.replace(location.origin + '/');
    } catch (error) {
      signingOut = false;
      if (disposed) return;
      button.disabled = false;
      button.textContent = 'Sign out';
      status.textContent = 'Could not sign out. Please try again.';
    }
  }

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
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = 'Sign out';
      button.className = 'infoflow-auth-action';
      button.onclick = () => signOut(button);
      controls.appendChild(button);
      return;
    }
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = nextMode === 'sign-in' ? 'Create an account' : 'Already have an account? Sign in';
    button.className = 'infoflow-auth-action';
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
    if (disposed || signingOut) return;
    if (!clerk.session) {
      if (mode !== 'sign-up') mount('sign-in');
      if (lastToken != null || data.authenticated) clearAuth();
      return;
    }
    mount('signed-in');
    const session = clerk.session;
    const revision = authRevision;
    const token = await session.getToken();
    if (disposed || signingOut || revision !== authRevision || clerk.session?.id !== session.id) return;
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
