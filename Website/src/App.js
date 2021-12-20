import {React, useEffect, useState} from "react"
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useLocation,
  useParams
} from "react-router-dom"
import Button from 'react-bootstrap/Button'
import Collapse from 'react-bootstrap/Collapse'

import Auth from "./modules/Auth"
import DiscordLogin from "./modules/DiscordLogin"
import Home from "./modules/Home"
import About from "./modules/About"
import Users from "./modules/Users"
import UserInfo from "./modules/UserInfo"
import GuildInfo from "./modules/UserInfo"

import './App.css';



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
  let auth_url = "https://discord.com/api/oauth2/authorize?response_type=token&client_id=847935658072604712&state=hi&scope=guilds%20identify"
  let state = "&state=hi" 

  const [guilds, setGuilds] = useState([])
  const [user, setUser] = useState([])

  useEffect(() => {
      let storage_user = localStorage.getItem('user')
      let storage_guilds = localStorage.getItem('guilds')
      console.log(storage_user)
      if (!!storage_user && !!storage_guilds){
        setUser(JSON.parse(storage_user))
        setGuilds(JSON.parse(storage_guilds))
        console.log("loaded user")
      }
  }, [])
  


  const get_global_user = () => user
  const set_global_user = (user) => setUser(user)

  const get_global_guilds = () => guilds
  const set_global_guilds = (guilds) => setGuilds(guilds)


  //logout = localStorage.removeItem('myData'); // or localStorage.clear();

  useEffect(() => {
    console.log(user)
    if (!!user){
      let storage_user = JSON.stringify(user)
      console.log(storage_user)
      localStorage.setItem('user', storage_user);
      console.log("wrote user")
    }
      
  }, [user])

  useEffect(() => {
    console.log(guilds)
    if (!!guilds){
      let storage_guilds = JSON.stringify(guilds)
      localStorage.setItem('guilds', storage_guilds);
      console.log("wrote guilds")
    }
      
  }, [guilds])

  const { hash } = useLocation()
  const hash_groups = hash.substr(1).split("&") // remove #
  const url_params = hash_groups.reduce(function(obj, x) {
      let [key, value] = x.split('=')
      obj[key] = value;
      return obj;
    }, {});
  return (
    <div>
      <div className="header">
        <div className="headerContent">
          <nav>
            <div className="left-header">
            <Link to="/">Home</Link>
            <Link to="/about">About</Link>
            <Link to="/users">Users</Link>
            </div>
            <div className="right-header">
              {user?user.username + "#" + user.discriminator :<a href={auth_url + state}>Authenticate with Discord</a>}
            </div>
          </nav>
        </div>
      </div>
      <div className="page">
        <div className="sideBar">
          <ul>
            <li>
              Getting Started
            </li>
            <li>
              Documentation
            </li>
            <li>
              {guilds.map(item => (
                  <li key={item.id}>
                      {item.owner? <img
                          style={{width:"20px"}}
                          src="https://cdn.icon-icons.com/icons2/2248/PNG/512/crown_icon_135729.png"
                          alt="Owner Icon"
                      />:null} 
                      <Link to={"/guilds/" + item.id}>{item.name}</Link>
                      {item.icon? <img
                          style={{width:"20px"}}
                          src={`https://cdn.discordapp.com/icons/${item.id}/${item.icon}.webp?size=128`}
                          alt="Owner Icon"
                      />:null} 
                      {item.permissions}<br/>
                      Admin:{(item.permissions&8)>0?"Yes":"No"} 
                  </li>
                  ))}
            </li>
          </ul>
        </div>
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
              <DiscordLogin 
                auth_params={url_params}
                userfunctions={[get_global_user, set_global_user]}
                guildfunctions={[get_global_guilds, set_global_guilds]}
              />
            </Route>
            <Route path="/oauth">
              <Auth 
                code={query.get("code")} 
                state={query.get("state")}
              />
            </Route>
            <Route path="/userinfo/:userid" children={
              <UserInfo
                userfunctions={[get_global_user, set_global_user]}
                guildfunctions={[get_global_guilds, set_global_guilds]}
              />
            }/>
            <Route path="/guilds/:guildid" children={
              <GuildInfo
                userfunctions={[get_global_user, set_global_user]}
                guildfunctions={[get_global_guilds, set_global_guilds]}
              />
            }/>
            <Route path="/">
              <Home /> {/* Catches everything not defined above */}
            </Route>
          </Switch>
        </div>
      </div>
    )
}