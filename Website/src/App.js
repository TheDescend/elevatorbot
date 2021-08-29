import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useLocation,
  useParams
} from "react-router-dom";

import Auth from "./modules/Auth"
import DiscordLogin from "./modules/DiscordLogin"

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
  let query = useQuery()
  let auth_url = "https://discord.com/api/oauth2/authorize?response_type=token&client_id=847935658072604712&state=hi&scope=guilds%20identify" //
  let state = "&state=hi" 
  const { hash } = useLocation();
  const hash_groups = hash.substr(1).split("&") // remove #
  const hash_obj = hash_groups.reduce(function(obj, x) {
      let [key, value] = x.split('=')
      obj[key] = value;
      return obj;
    }, {});
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
            <li>
              <a href={auth_url + state}>Authenticate with Discord</a>
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
          <Route path="/discordlogin">
            <DiscordLogin auth_params={hash_obj}/>
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