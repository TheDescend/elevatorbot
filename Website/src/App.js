import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useLocation
} from "react-router-dom";

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

function Auth({ code, state }) {
    //[discordID, serverID] = state.split(":")

    var url = 'https://www.bungie.net/platform/app/oauth/token/'
    var headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'authorization': 'Basic ' + Buffer.from("37440:rCCFPpK5jQezXen-gTJp7QqY6cZLbVBI7Rd6gkby-gQ").toString('base64'), //elevatortest credentials
        'origin': 'localhost:3000'
      }

    var data = `grant_type=authorization_code&code=${code}`


    //var time_now = Date.now();
    fetch(url, {
      method: "POST", 
      headers: headers,
      body: data
    }).then(res => {
      //TODO add error handling
      if (res.ok)
        backend_host = process.env.BACKEND_HOST
        backend_port = process.env.BACKEND_PORT
        var backend_url = `${backend_host}:${backend_port}/auth/bungie`
        fetch(backend_url, {
          method: "POST", 
          headers: {"hi": "Kigstn"},
          body: JSON.stringify({
            ...res,
            state: state
          })
        })
    });

  return <h3>These are not the html tags you are looking for</h3>
}