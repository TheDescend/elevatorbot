import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useLocation
} from "react-router-dom";

import Auth from "./modules/Auth"

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

export default function App() {
  return (
    <Router>
      <RouterFunc/>
    </Router>
  );
}

function RouterFunc(){
  let query = useQuery();
  return (
    <div>
        <nav>
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/about">About</Link>
            </li>
            <li>
              <Link to="/users">Users</Link>
            </li>
          </ul>
        </nav>

        {/* A <Switch> looks through its children <Route>s and
            renders the first one that matches the current URL. */}
        <Switch>
          <Route path="/about">
            <About />
          </Route>
          <Route path="/users">
            <Users />
          </Route>
          <Route path="/oauth">
            <Auth code={query.get("code")} state={query.get("state")}/>
          </Route>
          <Route path="/">
            <Home /> {/* Catches everything not defined above */}
          </Route>
        </Switch>
      </div>
    )
}

function Home() {
  return <h2>Home</h2>;
}

function About() {
  return <h2>About</h2>;
}

function Users() {
  return <h2>Users</h2>;
}